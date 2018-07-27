from rest_framework.serializers import HyperlinkedModelSerializer, Serializer,\
    ModelSerializer
from rest_framework.fields import IntegerField, URLField
from locations.models import Bookmark, Comment, Note, Like

class BookmarkManualSerializer(Serializer):
    id = IntegerField(read_only=True)
    link = URLField(required=False, max_length=1000)

    def create(self, validated_data):
        """
        Create and return a new `Bookmark` instance, given the validated data.
        """
        return Bookmark.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.url = validated_data.get('url', instance.url)
        instance.save()
        return instance


class CommentSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ['url', 'id', 'bookmark', 'time', 'text']


class CommentSerializerWithLikes(HyperlinkedModelSerializer):
    num_likes = IntegerField(read_only=True)
    class Meta:
        model = Comment
        fields = ['url', 'id', 'bookmark', 'time', 'text', 'num_likes']


class NoteSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Note
        fields = ['url', 'id', 'bookmark', 'time', 'text']

class BookmarkSerializer(ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'link']


class BookmarkLinkSerializer(HyperlinkedModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    notes = NoteSerializer(many=True, read_only=True)
    num_likes = IntegerField(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['url', 'id', 'link', 'comments', 'notes', 'num_likes']
