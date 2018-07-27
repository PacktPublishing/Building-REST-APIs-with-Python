from django.db import models
from django.db.models import Model
from django.db.models.fields import URLField, DateTimeField, TextField
from django.db.models.fields.related import ForeignKey
from django.db.utils import IntegrityError

# Create your models here.

class Bookmark(Model):
    link = URLField(max_length=1000, null=False, blank=False, db_index=True)

    def __str__(self):
        return str(self.link)


class Comment(Model):
    bookmark = ForeignKey(Bookmark, on_delete=models.CASCADE, related_name='comments')
    time = DateTimeField(auto_now_add=True, null=False, blank=True)
    text = TextField()

    def __str__(self):
        return self.text

    def link_str(self):
        return 'This comment: {} is for link: {}'.format(
            self.text, self.bookmark.link
        )

class Note(Model):
    bookmark = ForeignKey(Bookmark, on_delete=models.CASCADE, related_name='notes')
    time = DateTimeField(auto_now_add=True, null=False, blank=True)
    text = TextField()

    def __str__(self):
        return self.text


class Like(Model):
    bookmark = ForeignKey(
        Bookmark, on_delete=models.CASCADE, related_name='likes', null=True
    )
    comment = ForeignKey(
        Comment, on_delete=models.CASCADE, related_name='likes', null=True
    )

    def __str__(self):
        return '{} like'.format(
            self.bookmark.link if self.bookmark else self.comment.link
        )

    def clean(self):
        super().clean(self)
        if self.bookmark is None:
            if self.comment is None:
                raise IntegrityError(
                    'A like must be made to either a bookmark or a comment'
                )
        elif self.comment is not None:
            raise IntegrityError(
                'A like cannot be made to both a bookmark and a comment'
            )
