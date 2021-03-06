from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import FieldDoesNotExist

from rest_framework import serializers

from . import models


class ImageCropApplicationSerializer(serializers.ModelSerializer):
    field_label = serializers.SerializerMethodField('get_field_label')
    object_label = serializers.SerializerMethodField('get_object_label')
    content_type_label = serializers.SerializerMethodField('get_content_type_label')
    can_delete = serializers.SerializerMethodField('get_can_delete')

    def get_field_label(self, obj):
        if obj.object:
            try:
                return obj.object._meta.get_field_by_name(obj.field_name)[0].verbose_name
            except FieldDoesNotExist:
                return obj.field_name
        return None

    def get_object_label(self, obj):
        if obj.object:
            if hasattr(obj.object, 'get_mediacat_label'):
                return obj.object.get_mediacat_label()
            if isinstance(obj.object, ContentType):
                return obj.object.model_class()._meta.verbose_name_plural.title()

            return unicode(obj.object)
        return None

    def get_content_type_label(self, obj):
        if obj.object:
            return obj.object._meta.verbose_name.title()
        return None

    def get_can_delete(self, obj):
        if obj.object:
            try:
                field = obj.object._meta.get_field_by_name(obj.field_name)[0]
                return field.null
            except FieldDoesNotExist:
                return True
        return False


    class Meta:
        model = models.ImageCropApplication
        fields = (
            'id',
            'field_name',
            'content_type',
            'object_id',
            'field_label',
            'object_label',
            'content_type_label',
            'can_delete',
        )


class ImageCropSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField()
    ratio = serializers.SerializerMethodField('get_ratio')
    label = serializers.SerializerMethodField('get_label')
    applications = ImageCropApplicationSerializer(many=True, required=False)

    def get_ratio(self, obj):
        crop_info = settings.MEDIACAT_AVAILABLE_CROP_RATIOS[obj.key]
        return crop_info[1]

    def get_label(self, obj):
        crop_info = settings.MEDIACAT_AVAILABLE_CROP_RATIOS[obj.key]
        return crop_info[0]

    class Meta:
        model = models.ImageCrop
        fields = (
            'uuid',
            'image',
            'key',
            'ratio',
            'x1',
            'y1',
            'x2',
            'y2',
            'applications',
        )


class ImageAssociationSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField()
    content_type = serializers.PrimaryKeyRelatedField()
    object_label = serializers.SerializerMethodField('get_object_label')
    content_type_label = serializers.SerializerMethodField('get_content_type_label')

    def get_object_label(self, obj):
        if obj.object:
            if hasattr(obj.object, 'get_mediacat_label'):
                return obj.object.get_mediacat_label()
            if isinstance(obj.object, ContentType):
                return obj.object.model_class()._meta.verbose_name_plural.title()

            return unicode(obj.object)
        return None

    def get_content_type_label(self, obj):
        if obj.object:
            return obj.object._meta.verbose_name.title()
        return None

    class Meta:
        model = models.ImageAssociation
        fields = (
            'id',
            'content_type',
            'object_id',
            'canonical',
            'image',
            'object_label',
            'content_type_label',
        )


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.Field(source='get_original_url')
    thumbnail = serializers.Field(source='get_thumbnail_url')
    can_delete = serializers.Field(source='can_delete')

    class Meta:
        model = models.Image
        fields = (
            'id',
            'rank',
            'rating',
            'image_file',
            'date_created',
            'date_modified',
            'height',
            'width',
            'can_delete',
            'url',
            'thumbnail',
        )


class CategorySerializer(serializers.Serializer):

    name = serializers.CharField()
    content_type_id = serializers.IntegerField()
    object_id = serializers.IntegerField()
    count = serializers.IntegerField()
    path = serializers.CharField()
    children = serializers.SerializerMethodField('get_sub_categories')
    accepts_images = serializers.BooleanField()
    has_children = serializers.BooleanField()
    expanded = serializers.BooleanField()

    class Meta:
        fields = (
            'name',
            'content_type_id',
            'object_id',
            'count',
            'path',
            'accepts_images',
            'has_children',
            'children',
            'expanded',
        )

    def get_sub_categories(self, obj):
        if obj['children'] is None:
            return None
        return CategorySerializer(obj['children'], many=True).data
