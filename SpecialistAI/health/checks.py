# Function used to see if the provided user is an admin
def admin_check(user):
    # Return that they are
    return user.is_superuser