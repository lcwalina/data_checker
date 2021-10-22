import glob
import filecmp
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.mail import MailSender

class EmailOnChange(object):
    def __init__(self, destination, mailer):
        self.destination = destination
        self.mailer = mailer


    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool("EMAIL_ON_CHANGE_ENABLED"):
            raise NotConfigured

        destination = crawler.settings.get("EMAIL_ON_CHANGE_DESTINATION")
        if not destination:
            raise NotConfigured("EMAIL_ON_CHANGE_DESTINATION must be provided")

        mailer = MailSender.from_settings(crawler.settings)

        # Create an instance of our extension
        extension = cls(destination, mailer)

        crawler.signals.connect(extension.engine_stopped, signal=signals.engine_stopped)

        return extension
    
    def engine_stopped(self):
        # List out previous runs
        runs = sorted(glob.glob("/tmp/dataset/*.json"))

        if len(runs) < 2:
            return False
        # Compare them and if difference in the output, then send an email

        *_, previous, current = runs

        if not filecmp.cmp(previous, current):
            with open(current, "r") as f:
                self.mailer.send(
                    to=[self.destination],
                    subject="Datasets changed",
                    body="Changed in datasets detected, see the attachment for current datasets",
                    attachs=[(current.split("/")[-1], 'application/json', f)]
                )
        else:
            print("\n\n\n No change \n\n\n")