import site
site.addsitedir('/afs/athena.mit.edu/user/b/r/broder/lib/python2.5/site-packages')
import zephyr
from helper import custom_fill, tokenize
import traceback

class IO:
    def __init__(self, c = "dodona-test"):
        """
        Initializes the python-zephyr utilities.
        """
        self.cls = c
        # initialize zephyr
        zephyr.init()
        # subscribe to the specified cls
        zephyr.Subscriptions().add((self.cls, '*', '*'))
        # send an initialization message
        self.send(custom_fill('Dodona is now running.  If you find that a topic you wish answered is not accounted for, please send mail to dodona AT mit DOT edu'))

    def send(self, mess, name = None):
        """
        Sends a zephyr to the specified cls, addressing
        a specific person if specified.
        """
        if name != None:
            mess = name + ": " + mess

        mess = mess.decode("utf-8") # decode the message
        mess = custom_fill(mess)
        # try to send the message
        try:
            z = zephyr.ZNotice(cls=self.cls, fields=["", mess], sender='dodona@ATHENA.MIT.EDU')
            foo = str(z.__dict__)
            z.send()
        except KeyboardInterrupt:
            "Dodona is no longer running."
            raise
        except:
            print traceback.format_exc()

    def receive_from_subs(self, return_sender=False):
        """
        Receive a message from the cls specified in the 
        init method, and returns the message and the sender of the
        message if return_sender is True.
        """
        received = False
        while not received: # loop until you recieve a message
            try:
                m = zephyr.receive(True)
                received = True
            except KeyboardInterrupt:
                self.send("Dodona is no longer running.")
                raise
            except:
                continue

        # ignore messages from yourself
        while m.sender == 'dodona@ATHENA.MIT.EDU':
            try:
                m = zephyr.receive(True)
            except KeyboardInterrupt:
                self.send("Dodona is no longer running.")
                raise
            except:
                continue

        # ignore empty messages
        while m.__dict__['fields'][1].lower().strip() == "":
            try:
                m = zephyr.receive(True)
            except KeyboardInterrupt:
                self.send("Dodona is no longer running.")
                raise
            except:
                continue

        # ignore messages from anywhere except the specified
        # class
        while m.cls != self.cls:
            try:
                m = zephyr.receive(True)
            except KeyboardInterrupt:
                self.send("Dodona is no longer running.")
                raise
            except:
                continue

        print "From: ", m.sender
        print "Instance: ", m.instance
        print "Message: ", m.__dict__['fields'][1]

        sender = m.sender
        m = m.__dict__['fields'][1]
        # clean the message of trailing whitespce
        # and convert it to lowercase
        try:
            m = str(m.strip().lower())
        except KeyboardInterrupt:
            self.send("Dodona is no longer running.")
            raise
        except:
            print traceback.format_exc()

        if return_sender:  return [m, sender]
        else:  return m
