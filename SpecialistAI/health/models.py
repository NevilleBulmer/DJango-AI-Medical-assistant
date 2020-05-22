# Class responsible for all of the models which make up the application, I.e. user, medical information.
from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, Group

# If the user has an insurance company covering there treatment.
# then we user the Insurance model.
class Insurance(models.Model):
    # Instantiate variable policy_number and set it equal to model CharField functionality and pass max length.
    policy_number = models.CharField(max_length=200)
    # Instantiate variable company and set it equal to model CharField functionality and pass max length.
    company = models.CharField(max_length=200)
    # Function responsible for the repr, I.e. the medical insurance information.
    def __repr__(self):
        # Return the policy number and insurance comapny.
        return "{0} with {1}".format(self.policy_number, self.company)

# Model for EmergencyContact, Create emergency contact object.
class EmergencyContact(models.Model):
    # Instantiate variable first_name and set it equal to the models CharField functionality and pass a max length.
    first_name = models.CharField(max_length=20)
    # Instantiate variable last_name and set it equal to the models CharField functionality and pass a max length.
    last_name = models.CharField(max_length=20)
    # Instantiate variable phone_number and set it equal to the models CharField functionality and pass a max length.
    phone_number = models.CharField(max_length=30)
    # Instantiate variable relationship and set it equal to the models CharField functionality and pass a max length.
    relationship = models.CharField(max_length=30)

    # Function for returning a JSON objec.
    def json_object(self):
        # Return the EmergencyContact informaiton, I.e. fullname, telephone and relationship to patient.
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'relationship': self.relationship,
        }

# Model for MedicalInformation, Create medical information object.
class MedicalInformation(models.Model):
    # Instantiate array SEX_CHOICES and pass the relevant informaiton, I.e. the allowed sexes.
    SEX_CHOICES = (
        'Female',
        'Male',
        'Intersex',
    )
    # Instantiate variable sex and set it equal to the models CharField functionality and pass a max length.
    sex = models.CharField(max_length=50)
    # Instantiate variable insurance and set it equal to the models ForeignKey functionality and pass the Insurance object.
    insurance = models.ForeignKey(Insurance)
    # Instantiate variable medications and set it equal to the models CharField functionality and pass a max length and set null equal to true.
    medications = models.CharField(max_length=200, null=True)
    # Instantiate variable allergies and set it equal to the models CharField functionality and pass a max length and set null equal to true.
    allergies = models.CharField(max_length=200, null=True)
    # Instantiate variable medical_conditions and set it equal to the models CharField functionality and pass a max length and set null equal to true.
    medical_conditions = models.CharField(max_length=200, null=True)
    # Instantiate variable family_history and set it equal to the models CharField functionality and pass a max length and set null equal to true.
    family_history = models.CharField(max_length=200, null=True)
    # Instantiate variable additional_info and set it equal to the models CharField functionality and pass a max length and set null equal to true.
    additional_info = models.CharField(max_length=400, null=True)

    # Function for returning a JSON object.
    def json_object(self):
        # Return the medical informaiton, I.e. the sex, insurance informatio, medications etc.
        return {
            'sex': self.sex,
            'insurance': {
                'company': self.insurance.company,
                'policy_number':
                    self.insurance.policy_number
            },
            'medications': self.medications,
            'allergies': self.allergies,
            'medical_conditions':
                self.medical_conditions,
            'family_history': self.family_history,
            'additional_info': self.additional_info,
        }

    # Function responsible for the repr, I.e. the medical information.
    def __repr__(self):
        # Formats the returned medical information.
        return (("Sex: {0}, Insurance: {1}, Medications: {2}, Allergies: {3}, " +
                "Medical Conditions: {4}, Family History: {5}," +
                " Additional Info: {6}").format(
                    self.sex, repr(self.insurance), self.medications,
                    self.allergies, self.medical_conditions,
                    self.family_history, self.additional_info
                ))

# Model for hospital, Create hospital object.
class Hospital(models.Model):
    # Instantiate variable name and set it equal to the models CharField functionality and pass a max length.
    name = models.CharField(max_length=200)
    # Instantiate variable address and set it equal to the models CharField functionality and pass a max length.
    address = models.CharField(max_length=200)
    # Instantiate variable city and set it equal to the models CharField functionality and pass a max length.
    city = models.CharField(max_length=200)
    # Instantiate variable county and set it equal to the models CharField functionality and pass a max length.
    county = models.CharField(max_length=2)
    # Instantiate variable postal_code and set it equal to the models CharField functionality and pass a max length.
    postal_code = models.CharField(max_length=20)

    # Function responsible for returning a JSON object.
    def json_object(self):
        # Returns the hospiatal JSON object, I.e.
        # name, address, city, county and post code.
        return {
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'county': self.county,
            'postal_code': self.postal_code,
        }

    # Function responsible for returning the repr, I..e name, address etc.
    def __repr__(self):
        # Formats the returned hospital information.
        return ("%s at %s, %s, %s %s" % self.name, self.address, self.city,
                self.county, self.postal_code)

    # Function responsible for admission of a patient.
    def admit(self, user):
        # Instantiate variabel current_hospital_query and set it equal to the hospital stay 
        # object and pass the relevant information/arghuements, we pass
        # the user,
        # and we set the discharge__isnull to true, I.e. patient has been discharged.
        current_hospital_query = HospitalStay.objects.filter(patient=user,
            discharge__isnull=True)
        # If the current hospital stay exists, then the patient is currently in hospital.
        if current_hospital_query.exists():
            # For loop to iterate through the current hospital stays.
            for stay in current_hospital_query.all():
                # Set discharge equal to now, I.t. time and date to now.
                stay.discharge = timezone.now()
                # We save the stay.
                stay.save()
        # Call the hospital stay object and pass the relevant information/arguements,
        # the user,
        # and we set the discharge__isnull to true, I.e. patient has been discharged.
        HospitalStay.objects.create(patient=user, admission=timezone.now(),
                           hospital=self)

    # Function responsible for discharge of a patient.
    def discharge(self, user):
        # Instantiate user_query and se it equal to the hospital stay object and pass the relevant information/arguements,
        # sets patient equal to the user,
        # sets the hospital to self.
        user_query = HospitalStay.objects.filter(patient=user,
                                                hospital=self)
        # If the user query exists.
        if user_query.exists():
            # Set stay equal to the query first.
            stay = user_query.first()
            # sets the stay discharge equal to the current date and time.
            stay.discharge = timezone.now()
            # We save the stay.
            stay.save()

    # Function responsible for checking if a user is in a group.
    def users_in_group(self, group_name):
        # Return a list of all p[atient stays in stay.]
        return list({stay.patient for stay in
               HospitalStay.objects
                           .filter(hospital=self, patient__groups__name=group_name)
                           .distinct()
                           .order_by('patient__first_name', 'patient__last_name')
                           .all()})

# Model for user, Create user object.
class User(AbstractUser):
    # Instantiate variable date_of_birth and set it equal to the models DateField functionality.
    date_of_birth = models.DateField()
    # Instantiate variable phone_number and set it equal to the models CharField functionality 
    # and set a mas of 30 charactors.
    phone_number = models.CharField(max_length=30)
    # Instantiate variable medical_information and set it equal to the models ForeignKey and pass the medical 
    # informaiton along with setting null to true.
    medical_information = models.ForeignKey(MedicalInformation, null=True)
    # Instantiate variable emergency_contact and set it equal to the models ForeignKey and pass the emergency contact 
    # along with setting null to true.
    emergency_contact = models.ForeignKey(EmergencyContact, null=True)

    # Instantiate array REQUIRED_FIELDS and pass the relevant fields.
    REQUIRED_FIELDS = ['date_of_birth', 'phone_number', 'email', 'first_name',
                       'last_name', 'hospital']

    # Function for returning the patients.
    def all_patients(self):
        if self.is_superuser or self.is_doctor():
            # Admins and doctors can see all users as patients.
            return Group.objects.get(name='Patient').user_set.all()
        elif self.is_nurse():
            # Nurses get all users inside their hospital.
            return Group.objects.get(name='Patient').user_set.filter(hospital=self.hospital)
        else:
            # Users can only see themselves.
            return User.objects.filter(pk=self.pk)

    # Function responsible for checking if the user can edit a usuer.
    def can_edit_user(self, user):
        # Return user which is also checkjs the account type, I.e. a patient can edit theres but noone elses,
        # a doctor / super user can edit all.
        return user == self      \
            or self.is_superuser \
            or user.is_patient() \
            and self.is_doctor() or (self.is_nurse()
             and self.hospital == user.hospital)

    # Function responsible for checking if patients are active.
    def active_patients(self):
        # Return all active patients.
        return self.all_patients().filter(is_active=True)

    # Function responsible for checking if a logged in user can add prescription.
    def can_add_prescription(self):
        # Return id the user is either a super user or a doctor.
        return self.is_superuser or self.is_doctor()

    # Function responsible for retrieving latest message.
    def latest_messages(self):
        # Return the most recent message from a conversation.
        return self.sent_messages.order_by('-date')

    # Function responsible to retrieve and calculate the totla message count.
    def unread_message_count(self):
        # Return the message object and pass the relevant information/arguements, 
        # group members pk is set to the primary key of the group, I.e. id.
        # read members pk is set to the primary key of the read members, I.e. id.
        # distinct is set to the count of said messages.
        return Message.objects.filter(group__members__pk=self.pk)\
                              .exclude(read_members__pk=self.pk)\
                              .distinct().count()
    # Function responsible for returning appointments for the specified user.
    def schedule(self):
        # If the user is a super user.
        if self.is_superuser:
            # Return the appointments object, I.e. the appointment belonging to the user.
            return Appointment.objects
        # Else if the user is a doctor.
        elif self.is_doctor():
            # Doctors see all appointments for which they are needed.
            return Appointment.objects.filter(doctor=self)
        # Patients see all appointments
        return Appointment.objects.filter(patient=self)

    # Function responsible for returning the upcoming appointments, I.e. the future appointments.
    def upcoming_appointments(self):
        # Instantiate variable date and set it euqal to the time and date now.
        date = timezone.now()
        # Instantiate variable start_week and set it equal to the contents of variable now minus
        # date.weekday() to get the begining of a week.
        start_week = date - timedelta(date.weekday())
        # Instantiate variable end_week and set it equal to the contents of start_week plus
        # timedelta(7) to get the end of a week.
        end_week = start_week + timedelta(7)
        # Return the schedule for the whole week using variables start_week, end_week.
        return self.schedule().filter(date__range=[start_week, end_week])

    # Function responsible for checking if the user is part of the patients group, return true.
    def is_patient(self):
        # Return if the user is in the patient group or not.
        return self.is_in_group("Patient")

    # Function responsible for checking if the user is part of the nurse group, return true.
    def is_nurse(self):
        # Return if the user is in the nurse group or not.
        return self.is_in_group("Nurse")

    # Function responsible for checking if the user is part of the doctor group, return true.
    def is_doctor(self):
        # Return if the user is in the doctor group or not.
        return self.is_in_group("Doctor")

    # Function responsible for checking if the user is part of the admin group, return true.
    def is_admin(self):
        # Return if the user is in the patients group or not.
        return self.is_in_group("Admin")

    # Function responsible for checking if the user belongs to a group, return true if so.
    def is_in_group(self, group_name):
        # Try.
        try:
            # Return the group object and suplpy the relevant inforamtion/arguements,
            # name is set equal to the groups name,
            # apply a filter to make sure a primary key exists, I.e. id.
            return (Group.objects.get(name=group_name)
                         .user_set.filter(pk=self.pk).exists())
        # Except.
        except ValueError:
            # Return false.
            return False

    # Function responsible for returning a group.
    def group(self):
        # Returns the first element of a group.
        return self.groups.first()

    # Function responsible for checking if a given date and time is free to make a new appointment.
    def is_free(self, date, duration):
        # Instantiate variable schedule and set it equal to the schedule all.
        schedule = self.schedule().all()
        # instantiate variable end and set it equal the date plus the time delta in minutes.
        end = date + timedelta(minutes=duration)
        # Using a for loop to iterate through appointments in schedule, I.e. individual appointments.
        for appointment in schedule:
            # If the dates intersect (meaning one starts while the other is
            # in progress) then the person is not free at the provided date
            # and time.
            if (date <= appointment.date <= end or
                    appointment.date <= date <= appointment.end()):
                # Return false.
                return False
        # Return true.
        return True

    # Function responsible for checking if a user has any active prescriptions.
    def active_prescriptions(self):
        # Return the prescriptions and set a filter, returns all active prescriptions.
        return self.prescription_set.filter(active=True).all()
    # Function reesponsible for returning a JSON object
    def json_object(self):
        # Return the users informaiton, I.e. name, email, date of bith and phone number.
        json = {
            'name': self.get_full_name(),
            'email': self.email,
            'date_of_birth': self.date_of_birth.isoformat(),
            'phone_number': self.phone_number,
        }

        # If hospital, set the patients current hospital.
        if self.hospital:
            # Set the JSONS hospital equal to the current hospital json_object.
            json['hospital'] = self.hospital().json_object()
        # If medical informaiotn, set the patients mediacl information.
        if self.medical_information:
            # Set the JSONS medical information equal to the users medical information json_object.
            json['medical_information'] = self.medical_information.json_object()
        # If emergency contact, set the patients emergencycontact information.
        if self.emergency_contact:
            # Set the JSONS emergency contact equal to the users emergency contact json_object.
            json['emergency_contact'] = self.emergency_contact.json_object()
        # If prescriptions all.      
        if self.prescription_set.all():
            # Set the JSONS prescriptions equal to the users prescriptions json_object while iterating
            # through a prescriptions.
            json['prescriptions'] = [p.json_object() for p in
                self.prescription_set.all()]
        # If schedule, set the patients schedule.            
        if self.schedule():
            # Set the JSONS appointments to the users appointments json_object.
            json['appointments'] = [a.json_object() for a in self.schedule().all()]
        # Return the full json object which holds all of the informaiton from above.
        return json

    # Function responsible for hospital informaiton.
    def hospital(self):
        # Instantiate variable patient_query and set it equal to the hopspital stay 
        # object along with the relevant information/arguements,
        # patient is set to self,
        # discharge_isnull is set to true, I.e. no longer in hospital.
        patient_query = HospitalStay.objects.filter(patient=self,
                                                    discharge__isnull=True)
        # If the patient query exists.
        if patient_query.exists():
            # Instantiate variable stays and set it equl to the outcome of a for loop iterating through all patient quesries.
            stays = [x for x in patient_query.all()]
            # Return the stays array.
            return stays[0].hospital
        # Return none.
        return None

# Appointment model.
class Appointment(models.Model):
    # Instantiate variable patient and set it equal to models ForeignKey functionality and pass the related name as patients appointment.
    patient = models.ForeignKey(User, related_name='patient_appointments')
    # Instantiate variable doctor and set it equal to models ForeignKey functionality and pass the related name as doctors appointment.
    doctor = models.ForeignKey(User, related_name='doctor_appointments')
    # Instantiate variable date and set it equal to models DateTimeField functionality. 
    date = models.DateTimeField()
    # Instantiate variable duration and set it equal to models IntegerField functionality.
    duration = models.IntegerField()
    # Function responsible for getting the JSON.
    def json_object(self):
        # Return the JSON for a user with all relevant information.
        return {
            'date': self.date.isoformat(),
            'end': self.end().isoformat(),
            'patient': self.patient.get_full_name(),
            'doctor': self.doctor.get_full_name(),
        }

    # Function responsible for retrieving the enf, I.e. end of an appointment.
    def end(self):
        # Return the date plus the delta time in minutes.
        return self.date + timedelta(minutes=self.duration)
    # Function responsible for the repr, I.e. the duration, the date and who took part in the appointment.
    def __repr__(self):
        # Formats the returned medical information.
        return '{0} minutes on {1}, {2} with {3}'.format(self.duration, self.date,
                                                         self.patient, self.doctor)

# Hospital stay model.
class HospitalStay(models.Model):
    # instantiate variable patient and set it equal to the models ForeignKey functionality.
    patient = models.ForeignKey(User)
    # instantiate variable admission and set it equal to the models DateTimeField functionality.
    admission = models.DateTimeField()
    # instantiate variable discharge and set it equal to the models DateTimeField functionality and pass that null is true.
    discharge = models.DateTimeField(null=True)
    # instantiate variable hospital and set it equal to the models ForeignKey functionality.
    hospital = models.ForeignKey(Hospital)

# Prescription model.
class Prescription(models.Model):
    # Instantiate variable patient and set it equal to the models ForeignKey functioanlity and pass the user.
    patient = models.ForeignKey(User)
    # Instantiate variable name and set it equal to the models CharField functioanlity and pass the max length allowed.
    name = models.CharField(max_length=200)
    # Instantiate variable dosage and set it equal to the models CharField functioanlity and pass the max length allowed.
    dosage = models.CharField(max_length=200)
    # Instantiate variable directions and set it equal to the models CharField functioanlity and pass the max length allowed.
    directions = models.CharField(max_length=1000)
    # Instantiate variable prescribed and set it equal to the models DateTimeField functioanlity.
    prescribed = models.DateTimeField()
    # Instantiate variable active and set it equal to the models BooleanField functioanlity.
    active = models.BooleanField()

    # Function responsible for retrieving the JSON object.
    def json_object(self):
        # Return the JSON object for a prescription.
        return {
            'name': self.name,
            'dosage': self.dosage,
            'directions': self.directions,
            'prescribed': self.prescribed.isoformat(),
            'active': self.active
        }
    # Function responsible for the repr, I.e. the dosage, the name and the directions for a prescription.
    def __repr__(self):
        # Formats the returned medical information.
        return '{0} of {1}: {2}'.format(self.dosage, self.name, self.directions)

# Message group model.
class MessageGroup(models.Model):
    # Instantiate variable name and set it equal to the models CharField functionality and set a max length.
    name = models.CharField(max_length=140)
    # Instantiate variable members and set it equal to models ManyToManyField functionality and pass the user.
    members = models.ManyToManyField(User)

    # Function responsible for retrieving the latest message, I.e. the latest message within the conversation.
    def latest_message(self):
        # If the message count os equal to zero.
        if self.messages.count() == 0:
            # Return none.
            return None
        # Return all of the messages and order them by date and retrieving the first.
        return self.messages.order_by('-date').first()
    
    # Function responsible for retrieving the combined names for a conversations.
    def combined_names(self, full=False):
        # Instantiate variable names_count and set it equal to the count of members, I.e. the number of people in a conversation.
        names_count = self.members.count()
        # Instantiate variable extras and set it equal to the names count minus three.
        extras = names_count - 3
        # Instantiate variable members and set it equal to all members in a conversation.
        members = self.members.all()
        # If not full, I.e. if the conversation is not full.
        if not full:
            # Instantiate variable members and set itt equal to a members array.
            members = members[:3]
        # Instantiate variable names and set it equal to the result of the combined name and iterate
        # through the members.
        names = ", ".join([m.get_full_name() for m in members])
        # If extras is greater than zero and not full, I.e. there are members in the conversation
        # and it is not full.
        if extras > 0 and not full:
            # Set names either plus or equal to the extras if it is equal to one.
            names += " and %d other%s" % (extras, "" if extras == 1 else "s")
        # Return the names.
        return names

# Message model.
class Message(models.Model):
    # Instantiate variable sender and set it equal to models ForeignKey functionality, we pass the user and the 
    # related name to sent_message.
    sender = models.ForeignKey(User, related_name='sent_messages')
    # Instantiate variable group and set it equal to models ForeignKey functionality, we pass the message group and the 
    # related name to messages.
    group = models.ForeignKey(MessageGroup, related_name='messages')
    # Instantiate variable body and set it equal to the models TextField functionality.
    body = models.TextField()
    # Instantiate variable date and set it equal to the models DateTimeField.
    date = models.DateTimeField()
    # Instantiate variable read_members and set it equal to the models ManyToManyField functionality we pass the 
    # user and related name to read_messages. 
    read_members = models.ManyToManyField(User, related_name='read_messages')
    # Function responsible for loading the preview text for a message.
    def preview_text(self):
        # Return the preview of a message and limit the preview to 100 charactors.
        return (self.body[:100] + "...") if len(self.body) > 100 else self.body
