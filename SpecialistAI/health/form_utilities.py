# Class which is responsible for everything regarding forms, 
# I.e. sanitisation,
# email being valid,
# password matching and much more.
import re
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.admin import models
from django.contrib.contenttypes.models import ContentType
from django.utils.text import get_text_list

# Function responsible for sanitising telephone numbers.
def sanitize_phone(number):
    # If the variable number is not equal to a number.
    if not number:
        # Return none.
        return None
    # Else remove all none number characters.
    regex = re.compile(r'[^\d.]+')
    # Return the sanitised number variable.
    return regex.sub('', number)

# Function responsible for checking invalidness, I.e. if a field contains invalid informaiton.
def none_if_invalid(item):
    # Using the built in functionality of falseness of python, we check for false informaiotn.
    return item if bool(item) else None

# Function responsible for checking if an email address is valid.
def email_is_valid(email):
    # Try.
    try:
        # Using the in built validation functionality within DJango
        # we validate that the email provided meets the validation criteria.
        validators.validate_email(email)
        # If the above is successful, then return true.
        return True
    # Except, catch any error that occured.
    except ValidationError:
        # If the above is true, then return the error.
        return False

# Function responsible for checking if a message has been changed, 
# I.e. used for displaying changes to the admin account,
# used within the change method below.
def get_change_message(fields):
    # Return the changed fields.
    return 'Changed %s.' % get_text_list(fields, 'and')

# Function responsible for changing an object and logging it.
### Log that something was changed ###
def change(request, obj, message_or_fields):
    # The argument *message_or_fields* must be a sequence of modified field names
    # or a custom change message.

    # If the variable message_or_fields is an instance of a string, I.e. if the variable is of string type.
    if isinstance(message_or_fields, str):
        # Instantiate message and set it equal to the contents of message_or_fields.
        message = message_or_fields
    # Else.
    else:
        # Instantiate message and set it equal to the contents of message_or_fields usiong function 
        # get_change_message, I.e. checks if a message has changed.
        message = get_change_message(message_or_fields)
    
    # Using the models.LogEntry.objects.log_action functionality from DJango contrib main,
    # we log that somehting has changed and what that something is.
    # user_id set to the users primary key, I.e. id.
    # content_type_id sets the content_type_id equal to the objects priamry key.
    # object_id sets the objects primary key, I.e. id.
    # object_repr sets the repr to the object changed.
    # action_flag sets the action flag, I.e. something was changed.
    # change_message sets the change message, I.e. user (username) changed there telephone number.
    models.LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=repr(obj),
        action_flag=models.CHANGE,
        change_message=message
    )

# Function responsible for addition, I.e. specifying that something was added, 
# I.e. user (username) added a new message.
### Log that something was added ###
def addition(request, obj):
    # Using the models.LogEntry.objects.log_action functionality from DJango contrib main,
    # we log that somehting has changed and what that something is.
    # user_id set to the users primary key, I.e. id.
    # content_type_id sets the content_type_id equal to the objects priamry key.
    # object_id sets the objects primary key, I.e. id.
    # object_repr sets the repr to the object changed.
    # action_flag sets the action flag, I.e. something was added.
    models.LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=repr(obj),
        action_flag=models.ADDITION
    )

### Log that something was deleted ###
def deletion(request, obj, object_repr=None):
    # Using the models.LogEntry.objects.log_action functionality from DJango contrib main,
    # we log that somehting has changed and what that something is.
    # user_id set to the users primary key, I.e. id.
    # content_type_id sets the content_type_id equal to the objects priamry key.
    # object_id sets the objects primary key, I.e. id.
    # object_repr sets the repr to the object deleted.
    # action_flag sets the action flag, I.e. something was added.
    models.LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=object_repr or repr(obj),
        action_flag=models.DELETION
    )
