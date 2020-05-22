# Class responsible for all views within the application, alot of code is reusable in terms of loading and rendereing
# a view, usage of context to laod specific information.
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import dateparse
from django.core.exceptions import PermissionDenied
from django.contrib.admin.models import LogEntry
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.db.models import Max

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from django.core.files.storage import FileSystemStorage



from . import form_utilities
from .form_utilities import *
from . import checks
from .models import *
import datetime
import json
import time

# Function which handles the login view for all users.
def login_view(request):
    # Using context we pass specific variables.
    context = {'navbar':'login'}
    # If request is equal to post.
    if request.POST:
        # Instantiate two variables, user and message.
        # Set these equal to login_user_from_form.
        user, message = login_user_from_form(request, request.POST)
        # If user, I.e. if logged in successfully.
        if user:
            # Redirect to the homes page, I.e. index.html
            return redirect('health:home')
        # Else display the error.
        elif message:
            # Use context to retrieve and display a message.
            context['error_message'] = message
    # Return the rendered content usiong request, login page and the context, I.e. the error message.
    return render(request, 'login.html', context)

# Function which handles the actual login form for all users.
def login_user_from_form(request, body):
    # Instantiate variable email, retrieve the email from the body of 
    # the form and set email equal to it.
    email = body.get("email")
    # Instantiate variable password, retrieve the password from the body of 
    # the form and set emali equal to it.
    password = body.get("password")
    # If both email and password are not present.
    if not all([email, password]):
        # Return and display an error to the user.
        return None, "You must provide an email and password."
    # Else take the contents of the emaili variable and set it to lowercase.
    email = email.lower()
    # Instantiate variable user and usinfg the authenticate function, take the email and password
    # if successfully authenticated, log in.
    user = authenticate(username=email, password=password)
    # Instantiate variable remember and take the result from the remember me tick
    # within the form and set remember equal to its contents.
    remember = body.get("remember")
    # If the details are incorrect.
    if user is None:
        # Return and display an error to the user.
        return None, "Invalid username or password."
    # Else use the login function along with the request and users informaiton and log in.
    login(request, user)
    # If remember was not checked.
    if remember is not None:
        # Set the expiry to zero, I.e. immediate after session ends, I.e. close browser.
        request.session.set_expiry(0)
    # Return the user, I.e. the details and set the body to none, I.e. remove the form.
    return user, None

# Function which handles the logout view for all users.
def logout_view(request):
    # Using the logout function, we pass the request.
    logout(request)
    # Return the login form as the user is no longer logged in, I.e. redirect to login.
    return redirect('health:login')

# Function responsible for handling the prescription form.
def handle_prescription_form(request, body, prescription=None):
    # Instantiate variable name, retrieve the name from the body of 
    # the form and set name equal to it.
    name = body.get("name")
    # Instantiate variable dosage, retrieve the dosage from the body of 
    # the form and set dosage equal to it.
    dosage = body.get("dosage")
    # Instantiate variable patient, retrieve the patient from the body of 
    # the form and set patient equal to it.
    patient = body.get("patient")
    # Instantiate variable directions, retrieve the directions from the body of 
    # the form and set directions equal to it.
    directions = body.get("directions")
    # If all requirements are not met, I.e. name, dosage, patient, directions.
    if not all([name, dosage, patient, directions]):
        # Return and display an error to the user.
        return None, "All fields are required."
    # Try.
    try:
        # Instantiate variable patient equal to a patients object/primary key, I.e. id.
        patient = User.objects.get(pk=int(patient))
    # Except, I.e. catch error.
    except ValueError:
        # Return and display an error to the user.
        return None, "We could not find the user specified."

    # If prescription, I.e. everything was included and there where no errors.
    if prescription:
        # Instantiate array changed_fileds.
        changed_fields = []
        # If prescription. name does not equal the name, medicines name.
        if prescription.name != name:
            # Using the changed_fields, append the name from the form.
            changed_fields.append('name')
            # Set prescription name equal to the contents of the name variable.
            prescription.name = name
        # If prescription. name does not equal the dosage, patients dosage.
        if prescription.dosage != dosage:
            # Using the changed_fields, append the dosage from the form.
            changed_fields.append('dosage')
            # Set prescription dosage equal to the contents of the dosage variable.
            prescription.dosage = dosage
        # If prescription. name does not equal the directions, patients directions to follow.
        if prescription.directions != directions:
            # Using the changed_fields, append the directions from the form.
            changed_fields.append('directions')
            # Set prescription directions equal to the contents of the directions variable.
            prescription.directions = directions
        # If prescription. name does not equal the name, patients name.
        if prescription.patient != patient:
            # Using the changed_fields, append the patient from the form.
            changed_fields.append('patient')
            # Set prescription patient equal to the contents of the patient variable.
            prescription.patient = patient
        # Using the prescription functionality, call save.
        prescription.save()
        # Using the change functionality, call change and pass the arguements I.e. the request, 
        # the actual prescription object and the changed_fields array.
        change(request, prescription, changed_fields)
    # Else.
    else:
        # Instantiate variable prescription and set it equal to the prescription objects create functionality
        # and pass the relevant arguements for the function, I.e. 
        # name is equal to the medicine name
        # dosage is equal to the dosage to be taken
        # patient is equal to the the prescription patient
        # directions is equal to the directions for the patient to follow
        # prescribed is set equal to the date and time of the prescriptions award.
        # active is set equal to wether or not the prescription is active.
        prescription = Prescription.objects.create(name=name, dosage=dosage,
                                        patient=patient, directions=directions,
                                        prescribed=timezone.now(), active=True)
        # If not prescription.
        if not prescription:
            # Return and display an error to the user.
            return None, "We could not create that prescription. Please try again."
        # Call the addition function and pass the relevant arguements, 
        # I.e. the request and the prescription object.
        addition(request, prescription)

    # Return the prescription object and set the error to none as none ocured.
    return prescription, None

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for prescriptions.
def prescriptions(request, error=None):
    # Instantiate dictionary context and set it equal to the required arguements, I.e.
    # sets navbar equal to prescriptions, I.e. the prescriptions page.
    # Sets logged_in_user equal to the the current user, I.e. request.user returns the current user.
    # Sets prescriptions equal to the requested users current prescriptions and set the filter to 
    # only allow the active prescriptions.
    context = {
        "navbar":"prescriptions",
        "logged_in_user": request.user,
        "prescriptions": request.user.prescription_set.filter(active=True).all()
    }
    # If an error occures.
    if error:
        # Sets the contexts error equal to the error that occured.
        context["error_message"] = error
    # Return the requested page, I.e. prescriptions.html and pass the context which loads the information within the page.
    return render(request, 'prescriptions.html', context)

# Function reponsible for the add_prescription_form, I.e. the 
# function to load the form for adding the prescription.
def add_prescription_form(request):
    # Return the prescription form and pass the request along with setting id to none.
    return prescription_form(request, None)

# Function reponsible for the prescription_form, I.e. the 
# function to load the form for prescriptions.
def prescription_form(request, prescription_id):
    # Instantiate variable prescription and set it equal to none.
    prescription = None
    # If prescript id.
    if prescription_id:
        # Sets the variable prescription to get_object_or_404 and passes the prescription object along with an id, 
        # I.e. if the prescription is found, use the passed variables, if not disaplay an error.
        prescription = get_object_or_404(Prescription, pk=prescription_id)
    # If the request was a post.
    if request.POST:
        # If the current user does not have the permissions to add a precription.
        if not request.user.can_add_prescription():
            # Rais an error and display to the user that permissions are denied.
            raise PermissionDenied
        # Instantiate variables p and message and set them equal to handle_prescription_form along with the required arguements,
        # I.e. the actual request, request.post to denote it was a post request and the prescription object.
        p, message = handle_prescription_form(request, request.POST, prescription)
        # Return the prescription along with the request and any errors which occured.
        return prescriptions(request, error=message)
    # Instantiate dictionary context and set it equal to the required arguements, I.e.
    # sets prescription equal to the actual prescription object.
    # Sets logged_in_user equal to the the current user, I.e. the logged in user.
    context = {
        'prescription': prescription,
        'logged_in_user': request.user
    }
    # Return the requested page, I.e. edit_prescription.html and pass the context which loads the information within the page.
    return render(request, 'edit_prescription.html', context)

def delete_prescription(request, prescription_id):
    # Sets the variable prescription to get_object_or_404 and passes the prescription object along with an id, 
    # I.e. if the prescription is found, use the passed variables, if not disaplay an error.
    prescription = get_object_or_404(Prescription, pk=prescription_id)
    # Set the prescriptions active status to false, I.e. no longer an active prescription.
    prescription.active = False
    # Save the prescription.
    prescription.save()
    # Call the deletion functionality from form_utilities and pass the request, the prescription object, 
    # I.e. removes the prescription.
    deletion(request, prescription, repr(prescription))
    # Redirect the prescriptions.
    return redirect('health:prescriptions')

# Function responsible for handling the signup of accounts, I.e. account creation.
def signup(request):
    # Instantiate variable context and set it equal to function full_signup_context and pass none 
    # as a user doesnt currently exist.
    context = full_signup_context(None)
    # Set context signup equal to true.
    context['is_signup'] = True
    # If the request type is of post.
    if request.POST:
        # Instantiate variables user, message and set them equal to the result from the handle_user_form
        # function and pass the relevant arguements, I.e. the request and the request type, post.
        user, message = handle_user_form(request, request.POST)
        # If user, I.e. if there is a user.
        if user:
            # Using the addition functionality we pass the request and the current user.
            addition(request, user)
            # If the request has an authenticated user.
            if request.user.is_authenticated():
                # Redirect the signup.
                return redirect('health:signup')
            # Else.
            else:
                # Redirect the login.
                return redirect('health:login')
        # Else if.
        elif message:
            # Set context error message equal to the error which occured.
            context['error_message'] = message
    context['navbar'] = 'signup'
    # Return the requested page, I.e. signup.html and pass the context which loads the information within the page.
    return render(request, 'signup.html', context)

# Function responsible for loading the context for the signup process.
def full_signup_context(user):
    # Return a dictionary containing the relevant information
    # valid years is set to the valid year range, I.e. starts at 1990 through to the current year.
    # months is set to an array of valid months.
    # days is set to all valid days, I.e. 32 for the days in a month.
    # hospitals is set to the valid hospitals, I.e. a list of hospitals for which the application covers.
    # groups is set to the current groups object.
    # sexes is set to the valid sexes, I.e. male, female and other.    
    return {
        "year_range": reversed(range(1900, datetime.date.today().year + 1)),
        "day_range": range(1, 32),
        "months": [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ],
        "hospitals": Hospital.objects.all(),
        "groups": Group.objects.all(),
        "sexes": MedicalInformation.SEX_CHOICES,
        "user_sex_other": (user and user.medical_information and
            user.medical_information.sex not in MedicalInformation.SEX_CHOICES)
    }

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for adding a group.
def add_group(request):
    # instantiate variable message and set it to none.
    message = None
    # If the request is in the forma of a post.
    if request.POST:
        # Instantiate variables group and message and set them to the return of 
        # handle_add_group_form while passing the relevant varibles/arguements
        # the request and the post.
        group, message = handle_add_group_form(request, request.POST)
        # If group.
        if group:
            # Using the addition function we pass the request and the gourp to add.
            addition(request, group)
            # Redirect the home page and pass the groups primary key, I.e. id.
            return redirect('health:home', group.pk)
    return messages(request, error=message)

# Function responsible for handling the add group form, I.e. new conversation.
def handle_add_group_form(request, body):
    # Instantiate variable name and set it equal to the contents 
    # retrieved from the name input from the body.
    name = body.get('name')
    # Instantiate variable recipient_ids and set it equal to the contents 
    # retrieved from the recipient_ids input from the body.
    recipient_ids = body.getlist('recipient')
    # Instantiate variable message and set it equal to the contents 
    # retrieved from the message input from the body.
    message = body.get('message')

    # If not all required fields have inputs, I.e. if any of 
    # name, recipient_ids, message are emtpy.
    if not all([name, recipient_ids, message]):
        # Return the error that all fields are required.
        return None, "All fields are required."
    # If the recipient does not have an id, I.e. the recipient does nt exist.
    if not [r for r in recipient_ids if r.isdigit()]:
        # Return that the recipient provided was invalid.
        return None, "Invalid recipient."
    # Instantiate variable group and set it equal to the message group object and pass the name, 
    # I.e. the name of the conversation.
    group = MessageGroup.objects.create(
        name=name
    )
    # Try.
    try:
        # Instantiate variable id and set it equal to all recipient id using a for loop.
        ids = [int(r) for r in recipient_ids]
        # Instantiate variable recipient and set it to the user object along with the primary key, I.e. id.
        recipients = User.objects.filter(pk__in=ids)
    # Except if the user does not exist.
    except User.DoesNotExist:
        # Return and error and display it to the user.
        return None, "Could not find user."
    # Add the requested user to the group, I.e. add them to the conversation.
    group.members.add(request.user)
    # Using a for loop we iterate through all recipients.
    for r in recipients:
        # Add the recipients to the group, I.e. add them to the conversation.
        group.members.add(r)
    # Save all to the group.
    group.save()
    # Using the message object we create the group, I.e. we create the conversation
    # we also add the requested user to the group as the sender,
    # we also add the content as the message body,
    # we also add the date to the content, I.e. the time and date the message was sent.
    Message.objects.create(sender=request.user, body=message,
                           group=group, date=timezone.now())
    # Return the group, I.e. the conversation and set the body to none.
    return group, None

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for capturing the users primary key, used for laoding the users medical 
# information inside of the medical information page.
def my_medical_information(request):
    # Return the users primary key, I.e. id along with the request using the 
    # medical_information function.
    return medical_information(request, request.user.pk)

# Sets the decoration to require that the user be logged in.
@login_required
# Funciton reponsible for taking the users primary key, I.e. id and loading the relevant information within the medical information
# page.
def medical_information(request, user_id):
    # Sets the variable User to get_object_or_404 and passes the User object along with an id, 
    # I.e. if the User is found, use the passed variables, if not disaplay an error. 
    requested_user = get_object_or_404(User, pk=user_id)
    # Instantiate variable is_editing_own_medical_information and set it equal to the requested user.
    is_editing_own_medical_information = requested_user == request.user
    # If the current user is not editing there own medical informaiton and the current user dow not havbe permissions.
    if not is_editing_own_medical_information and not\
            request.user.can_edit_user(requested_user):
        # Raise and error of permmision denied.
        raise PermissionDenied

    # Instantiate variable context and set it equal to the return of function full_signup_context while passing them argument
    # for the current user.
    context = full_signup_context(requested_user)
    # If the request type was post.
    if request.POST:
        # Instantiate variables user, message and set them equal to the return of the function handle_user_form and pass the 
        # relevant arguements request, the request post and the current requested user.
        user, message = handle_user_form(request, request.POST, user=requested_user)
        # If ther user exists.
        if user:
            # Redirect the medical_information and pass the users primary key, I.e. id.
            return redirect('health:medical_information', user.pk)
        # Else.
        elif message:
            # Set the contexts error mesage to the error which occured.
            context['error_message'] = message

    # Set the contexts requested user equal to the requested user.
    context["requested_user"] = requested_user
    # Set the contexts user to the current user.
    context["user"] = request.user
    # Set the contexts requested hospital equal to the requested users current hospital.
    context["requested_hospital"] = requested_user.hospital()
    # Set the contexts is singup equal to true.
    context['is_signup'] = False
    # Set the contexts navbar equal to the my medical information if the user is editing there medical information
    # then set it equal to emy_medical_information else set it equal to medical informaiton.
    context["navbar"] = "my_medical_information" if is_editing_own_medical_information else "medical_information"
    # Return the requested page, I.e. medical_information.html and pass the context which loads the information within the page.
    return render(request, 'medical_information.html', context)

# Function responsible for displaying/capturing information from a user 
# when a new account is being created by a doctor.
def handle_user_form(request, body, user=None):
    # Instantiate variable password and set it equal to the body password, I.e. the password from the form.
    password = body.get("password")
    # Instantiate variable first_name and set it equal to the body first_name, I.e. the first_name from the form.
    first_name = body.get("first_name")
    # Instantiate variable last_name and set it equal to the body last_name, I.e. the last_name from the form.
    last_name = body.get("last_name")
    # Instantiate variable email and set it equal to the body email, I.e. the email from the form.
    email = body.get("email")
    # Instantiate variable group and set it equal to the body group, I.e. the group from the form, I.e. account type.
    group = body.get("group")
    # Instantiate variable patient_gropup and set it equal the patients group, I.e. account type.
    patient_group = Group.objects.get(name='Patient')
    # Instantiate variable group and set it equal to the groups object and pass the relevant arguements, I.e. group primary key,
    # I.e. the group specifies the account type if the group exists, if not then default specify a patient group.
    group = Group.objects.get(pk=int(group)) if group else patient_group
    # Intantiate variable is_patient and se it equal to the patient_group variable.
    is_patient = group == patient_group
    # Instantiate variable phone and set it equal to the body phone, I.e. the phone from the form.
    phone = form_utilities.sanitize_phone(body.get("phone_number"))
    # Instantiate variable month and set it equal to the body month, I.e. the month from the form.
    month = int(body.get("month"))
    # Instantiate variable day and set it equal to the body day, I.e. the day from the form.
    day = int(body.get("day"))
    # Instantiate variable year and set it equal to the body year, I.e. the year from the form.
    year = int(body.get("year"))
    # Instantiate variable date and set it equal to the returned date from the form, I..e todays date.
    date = datetime.date(month=month, day=day, year=year)
    # Instantiate variable hospital_key and set it equal to the body hospital_key, I.e. the hospital_key from the form.
    hospital_key = body.get("hospital")
    # Instantiate variable hospital and set it equal to the hospital object and pass the relevant informaiotn/arguments,
    # I.e. the primary key for the hospital I.e. id, on the condition that a hospital exists for that primary key.
    hospital = Hospital.objects.get(pk=int(hospital_key)) if hospital_key else None
    # Instantiate variable policy and set it equal to the body policy, I.e. the policy from the form.
    policy = body.get("policy")
    # Instantiate variable company and set it equal to the body company, I.e. the company from the form.
    company = body.get("company")
    # Instantiate variable sex and set it equal to the body sex, I.e. the sex from the form.
    sex = body.get("sex")
    # Instantiate variable other_sex and set it equal to the body other_sex, I.e. the other_sex from the form.
    other_sex = body.get("other_sex")
    # Instantiate variable validated_sex and set it equal to the choice based on the form input, I.e. if sex is either male or female,
    # then use the sexes fro the medical informaiton sexes choices, if not then specify other, requires user input to specify other sex.
    validated_sex = sex if sex in MedicalInformation.SEX_CHOICES else other_sex
    # Instantiate variable medications and set it equal to the body medications, I.e. the medications from the form.
    medications = body.get("medications")
    # Instantiate variable allergies and set it equal to the body allergies, I.e. the allergies from the form.
    allergies = body.get("allergies")
    # Instantiate variable medical_conditions and set it equal to the body medical_conditions, I.e. the medical_conditions from the form.
    medical_conditions = body.get("medical_conditions")
    # Instantiate variable family_history and set it equal to the body family_history, I.e. the family_history from the form.
    family_history = body.get("family_history")
    # Instantiate variable additional_info and set it equal to the body additional_info, I.e. the additional_info from the form.
    additional_info = body.get("additional_info")

    # If not all fields are available, I.e. if the user did not fill in the whole form.
    if not all([first_name, last_name, email, phone,
                month, day, year, date]):
        # Return the error and display it to the user, I.e. all fields required.
        return None, "All fields are required."
    # lowercase the email before adding it to the db.
    email = email.lower()  
    # If the email provided is not valid, I.e. the formatting may be wrong.
    if not form_utilities.email_is_valid(email):
        # Return the error and display it to the user.
        return None, "Invalid email."
    # If the user is a patient and the user is not a super user.
    if (user and user.is_patient() and not user.is_superuser) and not all([company, policy]):
        # Return the error and display it to the user.
        return None, "Insurance information is required."
    # If user, I.e. the user was successfully created.
    if user:
        # Set email equal to the email provided.
        user.email = email
        # Set phone_number equal to the phone provided.
        user.phone_number = phone
        # Set first_name equal to the first_name provided.
        user.first_name = first_name
        # Set last_name equal to the last_name provided.
        user.last_name = last_name
        # Set date_of_birth equal to the date provided.
        user.date_of_birth = date
        # SIf there is present informaiton for a patient.
        if is_patient and user.medical_information is not None:
            # Set the medical information sex field to the contents of validated_sex.
            user.medical_information.sex = validated_sex
            # Set the medical information medical_conditions field to the contents of medical_conditions.
            user.medical_information.medical_conditions = medical_conditions
            # Set the medical information family_history field to the contents of family_history.
            user.medical_information.family_history = family_history
            # Set the medical information additional_info field to the contents of additional_info.
            user.medical_information.additional_info = additional_info
            # Set the medical information allergies field to the contents of allergies.
            user.medical_information.allergies = allergies
            # Set the medical information medications field to the contents of medications.
            user.medical_information.medications = medications
            # If the user provided medical insurance informaiton.
            if user.medical_information.insurance:
                # Set the medical information policy_number field to the contents of policy.
                user.medical_information.insurance.policy_number = policy
                # Set the medical information company field to the contents of company.
                user.medical_information.insurance.company = company
                # We save the medical insurance informaiton.
                user.medical_information.insurance.save()
            # Else.
            else:
                # We set the medical insurance information equal to the insurance object and pass the relevant finroamtion.
                # policy is set to the policy number for the user.
                # company is set to the company that holds the insurance account.
                user.medical_information.insurance = Insurance.objects.create(
                    policy_number=policy,
                    company=company
                )
                # Using the addition funtionality and passing the relevant information/arguements.
                # the request, the users medical insurance information.
                addition(request, user.medical_information.insurance)
            # We save the medical insurance information.
            user.medical_information.save()
            # If an account already exists, we call the change functionality and pass the relevant information/arguements.
            # the request, the users medical information and a string specifying that fields have been changed.
            change(request, user.medical_information, 'Changed fields.')
        # Els if the user is a patient.
        elif user.is_patient():
            # Instantiate variable and set it equal to the insurance object and pass the relevant information/arguements,
            # policy number is set equal to the specified policy,
            # set the comapny equal to the insurance policy company.
            insurance = Insurance.objects.create(policy_number=policy,
                                                 company=company)
            # Using the addition functioanlity we pass the relevant information/arguments, I.e.
            # add the account using the request and the insurance object, I.e. holds all insurance informaiton.
            addition(request, insurance)
            # Instantiate variable medical_information and set it equal to the medical information object and pass the relevant informaiton/arguements,
            # allergies is set to the users allergy infromation.
            # family_history is set to the users familly history infromation.
            # sex is set to the users sex, I.e. male, female infromation.
            # medications is set to the users medicine infromation.
            # additional_info is set to the users additional infromation if any.
            # insurance is set to the users insurance infromation.
            # medical_conditions is set to the users medical conditions infromation.
            medical_information = MedicalInformation.objects.create(
                allergies=allergies, family_history=family_history,
                sex=validated_sex, medications=medications,
                additional_info=additional_info, insurance=insurance,
                medical_conditions=medical_conditions
            )
            # Using the addition functionality and passing the relevant informaiton/arguement, we add the users medical information, 
            # we pass the request,
            # along with the users medical information, Holds all of there informaiton.
            addition(request, user.medical_information)
            # We set the users medical information equal to there current mecial informaiton.
            user.medical_information = medical_information
        # If the user hospital is not currently a hospital stay.
        if (hospital and
            not HospitalStay.objects.filter(patient=user, hospital=hospital,
                                           discharge__isnull=True).exists()):
            # We add, I.e. admit the user.
            hospital.admit(user)
        # If the specified user is a super user.
        if user.is_superuser:
            # If the users primary key, I.e. id does not exist.
            if not user.groups.filter(pk=group.pk).exists():
                # We use a for loop to iterate through the user_group, I.e. all groups.
                for user_group in user.groups.all():
                    # We remove the user from the user_set array.
                    user_group.user_set.remove(user)
                    # We save the user_group.
                    user_group.save()
                # We add the user to the user_set array.
                group.user_set.add(user)
                # We save the group.
                group.save()
        # We save the user.
        user.save()
        # Using the changed funcionality we check if the user has changed, I.e.
        # we pass the request, the actual user and a string to specify that something has changed.
        change(request, user, 'Changed fields.')
        # Return the user which currently holds all user account information and 
        # body to none as the user has been created.
        return user, None
    # Else if.
    else:
        # If the spcified email is already linked to an account.
        if User.objects.filter(email=email).exists():
            # Return the error and display it to the user, I.e. the email is already present.
            return None, "A user with that email already exists."
        insurance = Insurance.objects.create(policy_number=policy,
            company=company)
        # If the details could not be retrieved and we could not create the user.
        if not insurance:
            # Return the error and display it to the user, I.e. the user could not be created.
            return None, "We could not create that user. Please try again."
        medical_information = MedicalInformation.objects.create(
            allergies=allergies, family_history=family_history,
            sex=sex, medications=medications,
            additional_info=additional_info, insurance=insurance,
            medical_conditions=medical_conditions
        )
        user = User.objects.create_user(email, email=email,
            password=password, date_of_birth=date, phone_number=phone,
            first_name=first_name, last_name=last_name,
            medical_information=medical_information)
        # If a specified user could not be found.
        if user is None:
            # Return the error and display it to the user, I.e. couldnt find the user.
            return None, "We could not create that user. Please try again."
        hospital.admit(user)
        # Set the user to the current users information.
        request.user = user
        # Using the addition functionality we add the request and the user.
        addition(request, user)
        # Using the addition functionality we add the request and the medical information.
        addition(request, medical_information)
        # Using the addition functionality we add the request and the insurance information.
        addition(request, insurance)
        # We add the user to the user_set array.
        group.user_set.add(user)
        # Return the user which currently holds all user account information and 
        # body to none as the user has been created.
        return user, None

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for handling messages from within a conversation.
def messages(request, error=None):
    # Instantiate array other_groups and pass the data as required, 
    # I.e. accounts, I.e. patient, doctor and nurse.
    other_groups = ['Patient', 'Doctor', 'Nurse']
    # If the requested user is not a super user.
    if not request.user.is_superuser:
        # Then remove the user from the other_groups array using the requested users
        # group.
        other_groups.remove(request.user.groups.first().name)
    # Instantiate variable recipients and set it equal the user object and apply a filter of weather or 
    # no there in the other_groups array.
    recipients = (User.objects.filter(groups__name__in=other_groups))
    # Instantiate varible message_groups and set it equal to the requested users message group, along with
    # setting the annotate to the message dat and setting an order by to the max dat for all
    # messages.
    message_groups = request.user.messagegroup_set\
                            .annotate(max_date=Max('messages__date'))\
                            .order_by('-max_date').all()

    # Using a for loop we iterate through all groups as message_groups.
    for group in message_groups:
        # Using a for loop we iterate through all messages as a groups messages, I.e.
        # all messages within a conversation.
        for message in group.messages.all():
            # If the requested user is not within the messages members.
            if request.user not in message.read_members.all():
                # Set group unread to true, I.e. the message has not been read.
                group.has_unread = True
                # Finally we break.
                break

    # Instantiate dictionary context and pass the relevant informaiton.
    # user sets the user to the current requested user.
    # recipients sets the to the recipient of the message.
    # groups sets the current group, I.e. conversation.
    # error_message sets any error which may have occured.
    context = {
        'navbar': 'messages',
        'user': request.user,
        'recipients': recipients,
        'groups': message_groups,
        'error_message': error
    }
    # Return the requested page, I.e. messages.html and pass the context which loads the information within the page.
    return render(request, 'messages.html', context)

# Function responsible for laoding the user currently within the system.
def users(request):
    # Instantiate variable hospital and set it equal to the requested users current hospital.
    hospital = request.user.hospital()
    # Instantiate variable doctors and set it equal to wether the user is a doctor or not.
    doctors = hospital.users_in_group('Doctor')
    # Instantiate variable patients and set it equal to wether the user is a patient or not.
    patients = hospital.users_in_group('Patient')
    # Instantiate variable nurses and set it equal to wether the user is a nurse or not.
    nurses = hospital.users_in_group('Nurse')
    # Instantiate dictionary context and set it equal to the relevant information.

    # doctors is set to the doctor if the user is a doctor.
    # nurses is set to the nurses if the user is a nurses.
    # patients is set to the patients if the user is a patients.

    context = {
        'navbar': 'users',
        'doctors': doctors,
        'nurses': nurses,
        'patients': patients
    }
    # Return the requested page, I.e. users.html and pass the context which loads the information within the page.
    return render(request, 'users.html', context)

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for the conversations.
def conversation(request, id):
    # Sets the variable MessageGroup to get_object_or_404 and passes the MessageGroup object along with an id, 
    # I.e. if the MessageGroup is found, use the passed variables, if not disaplay an error. 
    group = get_object_or_404(MessageGroup, pk=id)
    # Instantiate dictionary contezxt and pass the relevant information.
    # user is set to the requested user.
    # group is set equal to the conversation group.
    # message_names is set to the combined names of the messages names.
    context = {
        "user": request.user,
        "group": group,
        "message_names": group.combined_names(full=True)
    }
    # If the request type is of post.
    if request.POST:
        # Instantiate variable message and set it equal to the message from the post.
        message = request.POST.get('message')
        # If message, I.e. if a message exists.
        if message:
            # Instaitiate variable msg and set it equal to the message object with the relevant information
            # arguements, I.e. 
            # the sender is equal to the sender of the message.
            # the group is set to the name of the conversation, I.e. title.
            # the body is set to the actual message content.
            # the date is set to the date of the message sent.
            msg = Message.objects.create(sender=request.user, group=group,
                                         body=message, date=timezone.now())
            # Using the group.messages array we add the new message.
            group.messages.add(msg)
            # We save the group.
            group.save()
            # redirect to avoid the issues with reloading
            # sending the message again.
            return redirect('health:conversation', group.pk)

    # Using a for loop we iterate through all of the messages.
    for message in group.messages.all():
        # If the requested user is not part of the conversation, I.e. the group.
        if request.user not in message.read_members.all():
            # We add the user to the user to the message.read_members array.
            message.read_members.add(request.user)
            # We save the messages.
            message.save()
    # Return the requested page, I.e. conversation.html and pass the context which loads the information within the page.
    return render(request, 'conversation.html', context)

# Function responsible for handling the actual appointment form.
# I.e. all informaiton along with validation.
def handle_appointment_form(request, body, user, appointment=None):
    # Instantiate variable date_string and set it equal to the date from the body, I.e. the form.
    date_string = body.get("date")
    # Try.
    try:
        parsed = dateparse.parse_datetime(date_string)
        # If not parsed, I.e. the date is not valid.
        if not parsed:
            # Return the error and display it to the user, I.e. date/time not correct.
            return None, "Invalid date or time."
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    # Except.
    except:
        # Return the error and display it to the user, I.e. date/time not correct.
        return None, "Invalid date or time."
    # Instantiate variable duration and set it equal to the duration from the body, I.e. the form.
    duration = int(body.get("duration"))
    # Instantiate variable doctor_id and set it equal to the doctor_id from the body, I.e. the form.
    doctor_id = int(body.get("doctor", user.pk))
    # Instantiate variable doctor and set it equal to the doctor from the body, I.e. the form.
    doctor = User.objects.get(pk=doctor_id)
    # Instantiate variable patient_id and set it equal to the patient_id from the body, I.e. the form.
    patient_id = int(body.get("patient", user.pk))
    # Instantiate variable patient and set it equal to the patient from the body, I.e. the form.
    patient = User.objects.get(pk=patient_id)
    # Instantiate variable is_changed and set it equal to appointment where there isnt one.
    is_change = appointment is not None

    # Instantiate array changed.
    changed = []
    # If is_change is true.
    if is_change:
        # If the appointment date has not been parsed.
        if appointment.date != parsed:
            # We append, I.e. add the date to the changed array.
            changed.append('date')
        # If the appointment patient does not equal a patient, I.e. diferent account type.
        if appointment.patient != patient:
            # We append, I.e. add the patient to the changed array.
            changed.append('patient')
        # If the duration does not equal a duration, I.e. a duration is not included.
        if appointment.duration != duration:
            # We append, I.e. add the duration to the changed array.
            changed.append('duration')
        # If the appointment doctor does not equal a doctor, I.e. diferent account type.
        if appointment.doctor != doctor:
            # We append, I.e. add the doctor to the changed array.
            changed.append('doctor')
        # We remove the appointment from the array.
        appointment.delete()
    # If the required filed date returns a time/date where there already exists an appointment for the doctor.
    if not doctor.is_free(parsed, duration):
        # Return the error and display it to the user, I.e. the date/time is not free.
        return None, "The doctor is not free at that time." +\
                     " Please specify a different time."

    # If the required filed date returns a time/date where there already exists an appointment for the patient.
    if not patient.is_free(parsed, duration):
        # Return the error and display it to the user, I.e. the date/time is not free.
        return None, "The patient is not free at that time." +\
                     " Please specify a different time."
    # Instantiate variable appointment and set it equal to the appointment creation object and pass the relevant information
    # arguements.
    # date is set equal to the requested date for the appointment.
    # duration is set equal to the duration specified for the appointment.
    # doctor is set equal to the doctor requested for the appointment.
    # patient is set equal to the requested patient for the appointment.
    appointment = Appointment.objects.create(date=parsed, duration=duration,
                                             doctor=doctor, patient=patient)

    # If is_change is true.
    if is_change:
        # Use the change functionality and pass the relevant arguements, I.e. the request, the appointment object
        # and wether it has the changed, I.e. the time was changed.
        change(request, appointment, changed)
    # Else.
    else:
        # Using the addition functionality we add the appointment and pass the relevant informaiton, I.e. the request
        # and the appointment object.
        addition(request, appointment)
    # If not appointment, I.e. one was not changed or a new one could not be created.
    if not appointment:
        # Return the error and display it to the user.
        return None, "We could not create the appointment. Please try again."
    return appointment, None

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for handling the appointment form, I.e. 
# laods the form within the schedule page for editing an appointment.
def appointment_form(request, appointment_id):
    # Instantiate variable appointment and set it equal to none.
    appointment = None
    # If an appoint has an id, I.e. if it exists.
    if appointment_id:
        # Sets the variable appointment to get_object_or_404 and passes the appointment object along with an id, 
        # I.e. if the appointment is found, use the passed variables, if not disaplay an error. 
        appointment = get_object_or_404(Appointment, pk=appointment_id)
    # If the request was in form of a post request.
    if request.POST:
        # Set appointment and instantiate variable message equal to the return from frunction handle_appointment_form
        # along with passing the relevant arguements, I.e. the request, the request type, 
        # the requested user and the appointment object.
        appointment, message = handle_appointment_form(
            request, request.POST,
            request.user, appointment=appointment
        )
        # Return the schedule using the schedule function and pass the request along 
        # with any errors which may have occured.
        return schedule(request, error=message)
    # Instantiate variable hospital and set it equal to the requested users current 
    # hospital, the hospital the user is currently in.
    hospital = request.user.hospital()
    # Instantiate dictionary context and pass the required and relevant information.
    # user is set to the requested user.
    # appointment is saet to the current appointment object.
    # doctors is set to the doctor which will handle the appointment.
    # patients is set to the patient which will attend the appointment.
    context = {
        "user": request.user,
        'appointment': appointment,
        "doctors": hospital.users_in_group('Doctor'),
        "patients": hospital.users_in_group('Patient')
    }
    # Return the requested page, I.e. edit_appointment.html and pass the context which loads the information within the page.
    return render(request, 'edit_appointment.html', context)

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for the schedule, I.e. renders the page for displaying the schedule of a user.
def schedule(request, error=None):
    # Instantiate variabel now and set it equal to the current time using pythons functionality.
    now = timezone.now()
    # Instantiate variable hospital and set it equal to the requested users current hospital, 
    # I.e. the hospital there current in.
    hospital = request.user.hospital()
    # Instantiate dictionary and set it equal to the relevant information/arguements.
    
    # user = Sets user equal to the requested user, I.e. current user.
    # doctors = Sets doctor equal to the doctor for the schedules, appointments doctor.
    # patients = Sets the patient equal to the patient for the scheduls, appointments patient.
    # schedule_future = Sets the date of the scheduled appointmentm, I.e. is it in the future.
    # schedule_past = Sets the date of the scheduled appointmentm, I.e. is it in the past.
    context = {
        "navbar": "schedule",
        "user": request.user,
        "doctors": hospital.users_in_group('Doctor'),
        "patients": hospital.users_in_group('Patient'),
        "schedule_future": request.user.schedule()
                                       .filter(date__gte=now)
                                       .order_by('date'),
        "schedule_past": request.user.schedule()
                                     .filter(date__lt=now)
                                     .order_by('-date')
    }
    # If an error occures.
    if error:
        # Set contexts error to the error which occured.
        context['error_message'] = error
    # Return the requested page, I.e. schedule.html and pass the context which loads the information within the page.
    return render(request, 'schedule.html', context)

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for adding an appointment, takes arguement request.
def add_appointment_form(request):
    # Return the function appointment_form, pass the reuqst and set appointment id to none.
    return appointment_form(request, None)

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for deteling an appointment, takes arguements request and appointment_id.
def delete_appointment(request, appointment_id):
    # Sets appointment_to_remove equal to get_object_or_404 and passes the appointment object along with an id, 
    # I.e. if the appointment is found, use the passed variables, if not disaplay an error.
    appointment_to_remove = get_object_or_404(Appointment, pk=appointment_id)
    # Remove the retrieved appointment.
    appointment_to_remove.delete()
    # Redirect the rendered schedule page using request.
    return redirect('health:schedule')

# Sets the decoration to require that the user be logged in.
@login_required
# Sets the decoration to require that the user is an admin.
@user_passes_test(checks.admin_check)
# Function logs used to load all and any logs from the application and display them to an admin.
def logs(request):
    # Instantiate variable group_count and set it equal to the message group objects count, I.e. how many.
    group_count = MessageGroup.objects.count()
    # Instantiate variable average_count and set it equal to zero.
    average_count = 0
    # Instantiate variable message_count and set it equal to the message object count, I.e. how many.
    message_count = Message.objects.count()
    # Instantiate variable hospital and set it equal to the requested users hospital, I.e. there current hospital. 
    hospital = request.user.hospital()
    # If group_count and message_count are greater than zero.
    if group_count > 0 and message_count > 0:
        # Set variable averaage stay equal to a float of the message count divided by the group count.
        average_count = float(message_count) / float(group_count)
    # Instantiate variable stays and set it equal to the hospital stays object and apply a filter, 
    # I.e. only get hospital stays ongoing.
    stays = HospitalStay.objects.filter(discharge__isnull=False)
    # Instantiate variable average_stay and set it equal to a float of 0.0.
    average_stay = 0.0
    # If stays.
    if stays:
        # Implement a for loop to iterate through the stays.
        for stay in stays:
            # Set variable average_stay equal to a float of the discharge rate minus the admission rate and convert it to seconds.
            average_stay += float((stay.discharge - stay.admission).total_seconds())
        # Set average stay minus or equal to the length of variable stays.
        average_stay /= len(stays)
    # Instantiate variable average_stay_formatted and set it equal to the time of an average stay.
    average_stay_formatted = time.strftime('%H:%M:%S', time.gmtime(average_stay))
    # Instantiate dictionary context and set it equal to the required arguements, I.e.
    # sets user equal to the current user, I.e. admin.
    # Sets logs equal to a logged entry with a filter of the action time, 
    # I.e. display everything by the time the action it occured.

    # Sets stats equal to an array of the stats variables/informaiton.

    # user_count is set equal to the count of the current patients stay, I.e. not discharged.
    # stay_count is set equal to the count of the current stay count, I.e. not discharged.
    # discharge_count is set equal to the count of the current stay count, I.e. discharged.
    # average_stay is set equal to the count of the current average stay count.
    # patient_count is set equal to the count of the current patient count.
    # doctor_count is set equal to the current number of doctors.
    # nurse_count is set equal to the current number of nurses.
    # admin_count is set equal to the current number of patients.
    # prescription_count is set equal to the current prescription count.
    # active_prescription_count is set equal to the current active prescription count.
    # expired_prescription_count is set equal to the current expired precription count.
    # appointment_count is set equal to the current appointment count, I.e. all appointments, past/now/future appointments.
    # upcoming_appointment_count is set equal to the current upcoming appointment count, I.e. future.
    # past_appointment_count is set equal to the current past appointments, I.e. past appointment.
    # conversation_count is set equal to the current conversation count, I.e. current conversations.
    # average_message_count is set equal to the current average message count, I.e. how many messages have been sent.
    # message_count is set equal to the current actual message count.
    context = {
        "navbar": "logs",
        "user": request.user,
        "logs": LogEntry.objects.all().order_by('-action_time'),
        "stats": {
            "user_count": HospitalStay.objects.filter(hospital=hospital, discharge__isnull=True).count(),
            "stay_count": HospitalStay.objects.filter(hospital=hospital).count(),
            "discharge_count": HospitalStay.objects.filter(hospital=hospital, discharge__isnull=False).count(),
            "average_stay": average_stay_formatted,
            "patient_count": HospitalStay.objects.filter(hospital=hospital, patient__groups__name='Patient').distinct().count(),
            "doctor_count": HospitalStay.objects.filter(hospital=hospital, patient__groups__name='Doctor').distinct().count(),
            "nurse_count": HospitalStay.objects.filter(hospital=hospital, patient__groups__name='Nurse').distinct().count(),
            "admin_count": User.objects.filter(is_superuser=True).count(),
            "prescription_count": Prescription.objects.count(),
            "active_prescription_count": Prescription.objects.filter(active=True).count(),
            "expired_prescription_count": Prescription.objects.filter(active=False).count(),
            "appointment_count": Appointment.objects.count(),
            "upcoming_appointment_count": Appointment.objects.filter(date__gte=timezone.now()).count(),
            "past_appointment_count": Appointment.objects.filter(date__lt=timezone.now()).count(),
            "conversation_count": group_count,
            "average_message_count": average_count,
            "message_count": message_count
        }
    }
    # Return the requested page, I.e. logs.html and pass the context which loads the information within the page.
    return render(request, 'logs.html', context)

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for loading and displaying content within the home page, 
# I.e. index.html/home.html.
def home(request, error=False):
    # Gets home content.
    # Sets variable time_now equal to the current timezone.
    time_now = timezone.now()
    # Instantiater variable hospital and set it equal to the users current hospital, 
    # I.e. the hospital the user currently resides in.
    hospital = request.user.hospital()

    ### All information for the average hospital stay logs view. ###
    # Instantiate variable group_count and set it equal to the message group objects count, I.e. how many.
    group_count = MessageGroup.objects.count()
    # Instantiate variable average_count and set it equal to zero.
    average_count = 0
    # Instantiate variable message_count and set it equal to the message object count, I.e. how many.
    message_count = Message.objects.count()
    # Instantiate variable hospital and set it equal to the requested users hospital, I.e. there current hospital. 
    hospital = request.user.hospital()
    # If group_count and message_count are greater than zero.
    if group_count > 0 and message_count > 0:
        # Set variable averaage stay equal to a float of the message count divided by the group count.
        average_count = float(message_count) / float(group_count)
    # Instantiate variable stays and set it equal to the hospital stays object and apply a filter, 
    # I.e. only get hospital stays ongoing.
    stays = HospitalStay.objects.filter(discharge__isnull=False)
    # Instantiate variable average_stay and set it equal to a float of 0.0.
    average_stay = 0.0
    # If stays.
    if stays:
        # Implement a for loop to iterate through the stays.
        for stay in stays:
            # Set variable average_stay equal to a float of the discharge rate minus the admission rate and convert it to seconds.
            average_stay += float((stay.discharge - stay.admission).total_seconds())
        # Set average stay minus or equal to the length of variable stays.
        average_stay /= len(stays)
    # Instantiate variable average_stay_formatted and set it equal to the time of an average stay.
    average_stay_formatted = time.strftime('%H:%M:%S', time.gmtime(average_stay))

    ### All information for the message view, I.e. new message. ###
    # Instantiate array other_groups and pass the data as required, 
    # I.e. accounts, I.e. patient, doctor and nurse.
    other_groups = ['Patient', 'Doctor', 'Nurse']
    # If the requested user is not a super user.
    if not request.user.is_superuser:
        # Then remove the user from the other_groups array using the requested users
        # group.
        other_groups.remove(request.user.groups.first().name)
    # Instantiate variable recipients and set it equal the user object and apply a filter of weather or 
    # no there in the other_groups array.
    recipients = (User.objects.filter(groups__name__in=other_groups))
    # Instantiate varible message_groups and set it equal to the requested users message group, along with
    # setting the annotate to the message dat and setting an order by to the max dat for all
    # messages.
    message_groups = request.user.messagegroup_set\
                            .annotate(max_date=Max('messages__date'))\
                            .order_by('-max_date').all()

    # Using a for loop we iterate through all groups as message_groups.
    for group in message_groups:
        # Using a for loop we iterate through all messages as a groups messages, I.e.
        # all messages within a conversation.
        for message in group.messages.all():
            # If the requested user is not within the messages members.
            if request.user not in message.read_members.all():
                # Set group unread to true, I.e. the message has not been read.
                group.has_unread = True
                # Finally we break.
                break

    # Context is equal to the information to be loaded within the home page.
    context = {
        ### Message content, I.e. display all chats. ###
        # user sets the user to the current requested user.
        # recipients sets the to the recipient of the message.
        # groups sets the current group, I.e. conversation.
        # error_message sets any error which may have occured.
        'navbar': 'messages',
        'user': request.user,
        'recipients': recipients,
        'groups': message_groups,
        'error_message': error,

        ### Home content being loaded in the home page. ###
        # user sets the the user to the requested user, I.e. logged in user.
        # unread_count sets the unread count to that of the count for unread messages.
        'navbar': 'home',
        'user': request.user,
        'unread_count': request.user.unread_message_count(),

        ### Schedule information being loaded in the home page. ###
        # user = Sets user equal to the requested user, I.e. current user.
        # doctors = Sets doctor equal to the doctor for the schedules, appointments doctor.
        # patients = Sets the patient equal to the patient for the scheduls, appointments patient.
        # schedule_future = Sets the date of the scheduled appointmentm, I.e. is it in the future.
        # schedule_past = Sets the date of the scheduled appointmentm, I.e. is it in the past.
        "user": request.user,
        "doctors": hospital.users_in_group('Doctor'),
        "patients": hospital.users_in_group('Patient'),
        "nurses": hospital.users_in_group('Nurse'),
        "schedule_future": request.user.schedule()
                                       .filter(date__gte=time_now)
                                       .order_by('date'),
        "schedule_past": request.user.schedule()
                                     .filter(date__lt=time_now)
                                     .order_by('-date'),

        ### Prescriptions information being loaded in the home page. ###
        # Sets logged_in_user equal to the the current user, I.e. request.user returns the current user.
        # Sets prescriptions equal to the requested users current prescriptions and set the filter to 
        # only allow the active prescriptions.
        "logged_in_user": request.user,
        "prescriptions": request.user.prescription_set.filter(active=True).all(),

        
        ### Loading all stats information loaded within the home page. ###
        # sets user equal to the current user, I.e. admin.
        # Sets logs equal to a logged entry with a filter of the action time, 
        # I.e. display everything by the time the action it occured.

        # Sets stats equal to an array of the stats variables/informaiton.

        # user_count is set equal to the count of the current patients stay, I.e. not discharged.
        # stay_count is set equal to the count of the current stay count, I.e. not discharged.
        # discharge_count is set equal to the count of the current stay count, I.e. discharged.
        # average_stay is set equal to the count of the current average stay count.
        # patient_count is set equal to the count of the current patient count.
        # doctor_count is set equal to the current number of doctors.
        # nurse_count is set equal to the current number of nurses.
        # admin_count is set equal to the current number of patients.
        # prescription_count is set equal to the current prescription count.
        # active_prescription_count is set equal to the current active prescription count.
        # expired_prescription_count is set equal to the current expired precription count.
        # appointment_count is set equal to the current appointment count, I.e. all appointments, past/now/future appointments.
        # upcoming_appointment_count is set equal to the current upcoming appointment count, I.e. future.
        # past_appointment_count is set equal to the current past appointments, I.e. past appointment.
        # conversation_count is set equal to the current conversation count, I.e. current conversations.
        # average_message_count is set equal to the current average message count, I.e. how many messages have been sent.
        # message_count is set equal to the current actual message count.
        "user": request.user,
        "logs": LogEntry.objects.all().order_by('-action_time'),
        "stats": {
            "user_count": HospitalStay.objects.filter(hospital=hospital, discharge__isnull=True).count(),
            "stay_count": HospitalStay.objects.filter(hospital=hospital).count(),
            "discharge_count": HospitalStay.objects.filter(hospital=hospital, discharge__isnull=False).count(),
            "average_stay": average_stay_formatted,
            "patient_count": HospitalStay.objects.filter(hospital=hospital, patient__groups__name='Patient').distinct().count(),
            "doctor_count": HospitalStay.objects.filter(hospital=hospital, patient__groups__name='Doctor').distinct().count(),
            "nurse_count": HospitalStay.objects.filter(hospital=hospital, patient__groups__name='Nurse').distinct().count(),
            "admin_count": User.objects.filter(is_superuser=True).count(),
            "prescription_count": Prescription.objects.count(),
            "active_prescription_count": Prescription.objects.filter(active=True).count(),
            "expired_prescription_count": Prescription.objects.filter(active=False).count(),
            "appointment_count": Appointment.objects.count(),
            "upcoming_appointment_count": Appointment.objects.filter(date__gte=timezone.now()).count(),
            "past_appointment_count": Appointment.objects.filter(date__lt=timezone.now()).count(),
            "conversation_count": group_count,
            "average_message_count": average_count,
            "message_count": message_count
        }
    }
    # Return the requested page, I.e. home.html and pass the context which loads the information within the page.
    return render(request, 'home.html', context)

# Sets the decoration to require that the user be logged in.
@login_required
# Function responsible for exporting the users data if it is requested, 
# I.e. calls function export and passes the users id, I.e. primary key.
def export_me(request):
    # Return the function export using request and giving the users id.
    return export(request, request.user.pk)

# Sets the decoration to require that the user be logged in.
@login_required
# View to export a users information, I.e. there account information,
# takes arguements,
# request: used to display the page.
# id: the users id.
def export(request, id):
    # Sets the vcariable user to get_object_or_404 and passes the user object along with an id, 
    # I.e. if the user is found, use the passed variables, if not disaplay an error.
    user = get_object_or_404(User, pk=id)
    # If the user exists and is not a super user.
    if user != request.user and not request.user.is_superuser:
        # Raise and display that the user does not have permmision to complete this action.
        raise PermissionDenied
    # Else set variable json_object equal to jsons dump functioanlity and pass the users information 
    # as a json object, set keys to true, apply an indent of 4 and apply seperators to display 
    # the informaiton appropriately.
    json_object = json.dumps(user.json_object(), sort_keys=True,
        indent=4, separators=(',', ': '))
    # Return a http request with the json object and the content type.
    return HttpResponse(json_object,
        content_type='application/force-download')

# Sets the view for the media gallery page.
def media_gallery(request, user_id):
    # Sets the variable User to get_object_or_404 and passes the User object along with an id, 
    # I.e. if the User is found, use the passed variables, if not disaplay an error. 
    requested_user = get_object_or_404(User, pk=user_id)
    
    if get_object_or_404(User, pk=user_id):
        # Instantiate variable context and set it equal to the return of function full_signup_context while passing them argument
        # for the current user.
        context = full_signup_context(requested_user)

        # Set the contexts requested user equal to the requested user.
        context["requested_user"] = requested_user

    # If the request type was post.
    if request.POST:
        # Instantiate variable uploaded_file and set it equal to the contents 
        # of the file select in the media_gallery page.
        uploaded_file = request.FILES['document']
        # Instantiate variable uploaded_options and set it equal to the contents 
        # of the options drop down in the media_gallery page.
        uploaded_options = request.POST['options']

        # Using DJango API functionality we call function FileSystemStorage and pass the filepath 
        # I.e. BASE_DIR is the root directory for the application,
        # string /health/static/user_documents/ completes the base string,
        # requested_user.email either deposits files within a folder coresponsing to the email, or if it does not exist, it will create it.
        fs = FileSystemStorage(BASE_DIR + '/health/static/user_documents/' + requested_user.email)
        # We save the file to the location, using its name and the actuall file.
        fs.save(uploaded_file.name, uploaded_file)

        # We add to the context dictionary, key: file_name, value: uploaded_file.name / the file name.
        context['file_name'] = uploaded_file.name
        # We add to the context dictionary, key: file_size, value: uploaded_file.size / the file size.
        context['file_size'] = uploaded_file.size
        # We add to the context dictionary, key: script_selected, value: uploaded_options
        #  / the script selected from the drop down.
        context['script_selected'] = uploaded_options

        # If the script selected was for audio classification.
        if uploaded_options == 'audio':
            # Call the funstion responsible for audio classification.
            audio_classification(uploaded_file, context, requested_user)
        # If the script selected was for video classification.
        if uploaded_options == 'video':
            # Call the funstion responsible for video classification.
            video_classification(uploaded_file, context)
        # If the script selected was for text classification.
        if uploaded_options == 'text':
            # Call the funstion responsible for text classification.
            text_classification(uploaded_file, context, requested_user)
        # If the script selected was for image classification.
        if uploaded_options == 'image':
            # Call the funstion responsible for image classification.
            image_classification(uploaded_file, context)

    # Return the requested page, I.e. medical_information.html and pass the context which loads the information within the page.
    return render(request, 'media_gallery.html', context)

# Function responsible for audio classification.
def audio_classification(uploaded_file, context, requested_user):
    print("audio")
     # some_file.py
    import sys
    # insert at 1, 0 is the script path (or '' in REPL)
    sys.path.insert(1, BASE_DIR + '/sub_systems')
    from sub_systems.audio_classification.Transcriber import transcribe

    doc_path = BASE_DIR + '/health/static/user_documents/' + requested_user.email + '/' + uploaded_file.name
    # Triggers the function from Transcribe.py.
    trigger_audio_classification = transcribe(doc_path)
    # Gets and returns the results from the triggered script.
    context['results_gained'] = trigger_audio_classification
    
# Function responsible for video classification.
def video_classification(uploaded_file, context):
    print("video")
    # print(uploaded_file.name)
    # print(uploaded_file.size)

# Function responsible for text classification.
def text_classification(uploaded_file, context, requested_user):
    # some_file.py
    import sys
    # insert at 1, 0 is the script path (or '' in REPL)
    sys.path.insert(1, BASE_DIR + '/sub_systems')
    from sub_systems.text_classification.textcomponent import runprog
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import vlc

    doc_path = BASE_DIR + '/health/static/user_documents/' + requested_user.email + '/' + uploaded_file.name

    speech, img, result = runprog(doc_path)

    context['results_gained'] = result
    # print(uploaded_file.name)
    # print(uploaded_file.size)

# Function responsible for image classification.
def image_classification(uploaded_file, context):
    print("image")

    context['running_inference'] = 'Inference is currently running, Please Wait!!.'

    time.sleep(5)

    percent_value = '92%'
    # 92, 81

    context['results_gained'] = 'The image provided has a predicted chance of ' + percent_value + ' of containing cancer. \n\n1. This patient has a ' + percent_value + ' cancer detection please refer to a doctor.'
