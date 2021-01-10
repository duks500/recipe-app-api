from django.db import models
# what we need to extand the user base model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


# extends the BaseUserManager
# Helo manage user and superuser
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a new user"""
        # Rasie an error if the email is empty
        if not email:
            raise ValueError('User must have an email address')
        # Make the email to be lower case for every new user
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and saves a new super user"""
        # Create a new user using create_user
        user = self.create_user(email, password)
        user.is_staff = True
        # Make the user to be a superuser
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that suppors using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # create new user manager for the objects
    objects = UserManager()

    # make the default username to be email insead of name
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        # The model for the foreignKey
        settings.AUTH_USER_MODEL,
        # on_delete= What to do after deleting the user
        # In this case, delete the tag
        on_delete=models.CASCADE,
    )

    def __str__(self):
        # return the string representation
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        # The model for the foreignKey
        settings.AUTH_USER_MODEL,
        # on_delete= What to do after deleting the user
        # In this case, delete the tag
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
