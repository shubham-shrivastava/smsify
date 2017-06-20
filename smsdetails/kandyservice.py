from Kandy import *
#import pprint
#pp = pprint.PrettyPrinter(indent=4)
from django.shortcuts import render, redirect


class SMS:
    domain_api_key = None
    domain_secret = None
    user_id = None

    user_access_token = None
    device_id = None

    #   Check user auth details
    def check_init_error(self, domain_api_key, domain_secret, user_id):
        if not domain_api_key:
            raise ValueError('Invalid domain key.')
        if not domain_secret:
            raise ValueError('Invalid domain secret.')
        if not user_id:
            raise ValueError('Invalid user ID.')

    #   Constructor
    def __init__(self, domain_api_key, domain_secret, user_id):
        self.check_init_error(domain_api_key, domain_secret, user_id)
        self.domain_api_key = domain_api_key
        self.domain_secret = domain_secret
        self.user_id = user_id

        #   Get user access token
        print("Getting User Access Token")
        data = User.get_user_access_token(
            self.domain_api_key, self.domain_secret, self.user_id)
        if data and data['status'] == 0 and data['result'] and data['result']['user_access_token']:
            self.user_access_token = data['result']['user_access_token']
            print("User Access Token: " + self.user_access_token)
        else:
            err = "Server replied with invalid User Access Token."
            raise ValueError(err)
        print('')

        print("Getting Device ID")
        data = User.get_devices(self.user_access_token)
        if data and data['result'] and data['result']['devices'] and data['result']['devices'][0] and data['result']['devices'][0]['id']:
            self.device_id = data['result']['devices'][0]['id']
            print("Device ID: " + self.device_id)
        else:
            err = "Server replied with invalid User Access Token."
            raise ValueError(err)
        print('')

    #   Send SMS
    def send(self, source, destination, text):
        if not self.device_id:
            raise ValueError('Invalid device ID.')

        #   Actual sending
        print("Sending SMS")
        data = Device.send_sms(self.user_access_token,
                               self.device_id, source, destination, text)
        if data and data['status'] == 0:
            print("SMS sent successfully!")
            return True
        else:
            return False
            # err = "Could not send SMS."
            # return render(request, 'sendmessage.html',
            #               {'form': form, 'error': 'Problem with API, Could not send.'})
            # raise ValueError(err)


# def main():
#     domain_api_key = "DAKb452d7f3dc3647788008c6f27fbf0d40"
#     domain_secret = "DAS016c34a169e1498f801ef68a7cdab9a1"
#     user_id = "shubham"

#     source_phone_number = "+918236028730"
#     destination_phone_number = "+919511727469"
#     message = "Hello Shubham"

#     try:
#         sms = SMS(domain_api_key, domain_secret, user_id)
#         sms.send(source_phone_number, destination_phone_number, message)
#     except Exception as e:
#         print('Error: ' + str(e))


# if __name__ == "__main__":
#     main()
