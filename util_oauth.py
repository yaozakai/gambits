# OAUTH signature creator

import hashlib
import hmac
import urllib
from random import getrandbits

from constants import TWITTER_CONSUMER_KEY_SECRET


class OAuthSignature():

    # Twitter API url
    url = ""

    # User secret keys
    secrets = {
        'consumer_secret': "",
        'token_secret': ""
    }

    def generate(self, params):
        """
        Generate Twitter signature
        """

        # Step 1. Collecting parameters
        params_str = '&'.join(
            [('%s=%s' % (self.encode(str(k)), self.encode(str(params[k])))) for k in sorted(params)])

        # Step 2. Creating the signature base string
        # Join the entire message together per the OAuth specification.
        message = "&".join(
            [self.encode("POST"), self.encode(self.url), self.encode(params_str)])

        # Step 3. Getting a signing key
        # consumer secret key
        cSecret = self.encode(self.secrets.get('consumer_secret'))

        # consumer key
        tSecret = self.encode(self.secrets.get('token_secret'))

        # The signing key is simply the percent encoded consumer secret,
        # followed by an ampersand character,
        # followed by the percent encoded token secret
        key = "%s&%s" % (cSecret, tSecret)

        # Step 4. Calculating the signature
        # Create a HMAC-SHA1 signature of the message.
        signature = hmac.new(b'key', message, hashlib.sha1).digest()

        digestBase64 = signature.encode("base64").rstrip('\n')

        return digestBase64

    def nonce(self):
        """ Generate random nonce value"""
        return str(getrandbits(64))

    def encode(self, text):
        return urllib.parse.quote(str(text), "")
