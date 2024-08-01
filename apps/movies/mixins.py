from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from django.db.models import Q, ForeignKey
from django.forms import ValidationError
from django.db.models import Q

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache

from django.db import models

from django.utils.translation import gettext_lazy as _

class CacheMixin:
    cache_timeout = 60 * 30

    def get_cache_key(self, request, *args, **kwargs):
        return f"{request.path}-{request.user.id}"

    def get(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request, *args, **kwargs)
        response = cache.get(cache_key)
        if response is None:
            response = super().get(request, *args, **kwargs)
            cache.set(cache_key, response, self.cache_timeout)
        return response


class CustomPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    # We won't set a default page_size here since it will be dynamic

    def paginate_queryset(self, queryset, request, view=None):
        # Check if a page number is provided in the request
        page_number = request.query_params.get(self.page_query_param)
        try:
            self.page_size = int(
                request.query_params.get(self.page_size_query_param, self.page_size)
            )
        except (TypeError, ValueError):
            self.page_size = self.get_default_page_size()

        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data, count):
        return JsonResponse(
            {
                "count": count,
                "next": None if count == 0 else self.get_next_link(),
                "previous": None if count == 0 else self.get_previous_link(),
                "results": data,
            },
            safe=False,
            status=status.HTTP_200_OK,
        )


class MixinsList(CacheMixin):
    model = None
    class_serializer = None
    permission_get = None
    permission_post = None
    responses = None

    permission_classes = [permission_get]

    def get(self, request, *args, **kwargs):
        """
        List all objects of model \n
        page_size: number of objects per page (default: 25) \n
        active: filter by active status (default: no apply filter, true: active, false: inactive) \n
        """

        active = request.query_params.get("active", None)
        query = request.query_params.get("query", "")
        order = request.query_params.get("order", "created_at")
        if order not in [field.name for field in self.model._meta.fields]:
            order = "created_at"

        exclude_fields = ["id", "is_active", "created_at", "updated_at"]
        # add foreign key fields to exclude_fields
        for field in self.model._meta.fields:
            if isinstance(field, ForeignKey):
                exclude_fields.append(field.name)
                
        query_filter = Q()
        for field in self.model._meta.fields:
            if field.name not in exclude_fields:
                query_filter |= Q(**{f"{field.name}__icontains": query})                

        if active is not None:
            active = True if active.lower() == "true" else False
            objects = (
                self.model.objects.filter(is_active=bool(active))
                .filter(query_filter)
                .order_by(order)
            )
        else:
            objects = self.model.objects.filter(query_filter).order_by(order)

        total_count = objects.count()
        paginator = CustomPagination()
        page = paginator.paginate_queryset(objects, request)

        if page is not None:
            serializers = self.class_serializer(page, many=True)
            return paginator.get_paginated_response(serializers.data, total_count)
        elif total_count == 0:
            return paginator.get_paginated_response([], total_count)
    
        return JsonResponse(
                {"detail": _("Invalid page.")},
                safe=False, 
                status=status.HTTP_404_NOT_FOUND
            )

    permission_classes = [permission_post]

    def post(self, request):
        """
        Create a new object of model
        """
        # serializes data entry
        objSerializer = self.class_serializer(data=request.data)
        # verify if entry is valid
        if objSerializer.is_valid():
            # save entry
            objSerializer.save()
            # show object saved
            return JsonResponse(
                objSerializer.data, 
                safe=False, 
                status=status.HTTP_201_CREATED
            )
        # show errors because not save
        return JsonResponse(
            objSerializer.errors, 
            safe=False, 
            status=status.HTTP_400_BAD_REQUEST
        )


class MixinOperations(CacheMixin):
    model = None
    class_serializer = None
    permission_get = None
    permission_post = None
    permission_put = None
    permission_delete = None

    def get(self, request, id):
        """
        Show one objects of any model by his id
        """
        # Search object by id
        obj = get_object_or_404(self.model, id=id)
        # serializes object
        serializer = self.class_serializer(obj, many=False)
        # show object
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    

    permission_classes = [permission_post]

    def post(self, request, id):
        """
        Active one object of model by his id
        """
        obj = get_object_or_404(self.model, id=id)
        if not obj.is_active:
            # serializes data entry
            obj.is_active = True
            # save entry
            obj.save()
            # show blank object (deleted)
            serializer = self.class_serializer(obj)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        # show errors because user is inactive                    
        return JsonResponse(
            {"detail": _(f"This {self.model.__name__} is active")}, 
            safe=False, 
            status=status.HTTP_400_BAD_REQUEST
        )
    

    permission_classes = [permission_put]

    def put(self, request, id):
        """
        Edit one objects of model by his id
        """
        # Search object by id
        obj = get_object_or_404(self.model, id=id)
        # serializes data entry
        serializer = self.class_serializer(obj, data=request.data)

        # verify if entry is valid
        if serializer.is_valid():
            # save entry
            serializer.save()
            # show object updated
            return JsonResponse(
                serializer.data, safe=False, status=status.HTTP_202_ACCEPTED
            )
        # show errors because not save        
        return JsonResponse(
            serializer.errors, 
            safe=False, 
            status=status.HTTP_400_BAD_REQUEST
        )
       
    permission_classes = [permission_delete]

    def delete(self, request, id):
        """
        Delete one objects of model by his id \n
        realy never delete, only change status to inactive
        """
        # Search object by id
        obj = get_object_or_404(self.model, id=id)
        if obj.is_active:
            # user can be deleted only status inactive
            obj.is_active = False
            obj.save()
            serializer = self.class_serializer(obj)
            # show blank object (deleted)
            return JsonResponse(
                serializer.data, safe=False, status=status.HTTP_202_ACCEPTED
            )
            # show errors because user is inactive
        return JsonResponse(
            {"message": _(f"This {self.model.__name__} is inactive")}, 
            safe=False, 
            status=status.HTTP_400_BAD_REQUEST
        )
        