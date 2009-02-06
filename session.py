import site
site.addsitedir('/afs/athena.mit.edu/user/b/r/broder/lib/python2.5/site-packages')

import zephyr
from zephyrUI import send
from fuzzystack import FuzzyStack
from helper import print_list, custom_list, tokenize, integrate_lists, find_partial_key 
from xml_parser import update_files

#######################################
# The Session class stores a "session",
# or conversation, between Dodona and
# the user.
#######################################

class Session:
    def __init__(self, name, topics):
        self.memory = FuzzyStack(20)
        self.memory.push("data", topics)
        self.memory.push("name", name)
        self.name = name
        self.topics = topics

    def AI(self, mess, d = self.topics):
        """
        Determines the keywords in the message,
        and returns either:
            - a list of keys, if there is more than one
            - a single key
            - the status "d:none", if there are none
        """
        mess = tokenize(mess)
        keys = []
        for key in mess:
            integrate_lists(keys, find_partial_key(key, d))
        if len(keys) > 1:
            return keys
        elif len(keys) == 0:
            return "d:none"
        else:
            return keys[0]    

    def add_data(self, mess, newtopic):
        """
        Adds a piece of new data to Dodona's 
        knowledge, after having ascertained the 
        subtopic and topic.

        Corresponds to the status add_data_true or
        add_data_false, depending on whether the
        topic is brand new or not, respectively.
        """
        subtopic = self.memory.pop("topic")[1]
        topic = self.memory.pop("topic")[1]
        print topics[topic]
        topics[topic][subtopic] =  mess
        if newtopic: update_files(topic, topics)
        else: update_files(topic, topics, False)
        send("Thanks!", self.name)
        return False

    def sub_topic(self, mess, subtopic = None):
        """
        Part of Dodona's learning algorithm.
        Determines the subtopic, and waits for
        the user to give it information about
        that subtopic and topic.

        Corresponds to the status subtopic.
        """
        topic = self.memory.read("topic")
        # if the subtopic is not already known, then
        # read it from the current message.  This is
        # an indicator that the topic is new or not.
        if subtopic == None:
            subtopic = mess
            newtopic = True
        else:
            newtopic = False

        send("Ok, we are talking about " + subtopic + " under " + topic + "!  Please tell me all you know about " + subtopic + " under " + topic + ".", self.name)
        self.memory.push("topic", subtopic)

        # if the topic is new, then set the status to add_data_true
        if newtopic:  self.memory.push("status", "add_data_true")
        # if it's not, then set the status to add_data_false
        else:  self.memory.push("status", "add_data_false")

        return None

    def learn(self):
        """
        Begins the learning process.  Determines the topic
        to which new information will be added.  If the user
        is already talking about a topic, and tells Dodona
        something she doesn't understand, then this will be
        the subtopic.  If not, then she prompts the user to
        enter a subtopic.
        """
        name = self.name
        subtopic = self.memory.pop("topic")[1]
        topic = self.memory.pop("topic")
        # if the topic is foreign, then prompt the user
        # for a subtopic and set the status to subtopic
        if topic == False:
            topic = subtopic
            topics[subtopic] = {}
            send("What subtopic under " + topic + " would you like to tell me about?", name)
            self.memory.push("topic", topic)
            self.memory.pop("status")
            self.memory.push("status", "subtopic")
            return None
        # if not, then go directly to sub_topic
        else:
            self.memory.push("topic", topic[1])
            return self.sub_topic("", subtopic)

    def unknown(self, mess):
        """
        Called when Dodona encounters something she does
        not understand.  Asks the user if he/she would
        like to tell Dodona about the subject.

        Corresponds to the status unknown.
        """
        name = self.name
        # if the user says yes, then call learn
        if mess.find("yes") != -1:
            self.learn()
            return None
        
        # if the user says no, and you're already
        # talking about a specific topic, then ask if
        # the user wants to continue talking about it,
        # and sets the status to conv_topic
        # if not, then return False (reset the session)
        if mess.find("no") != -1:
            send("Ok.", name)
            self.memory.pop("topic")
            t = self.memory.read("topic")
            self.memory.pop("status")
            if t == None:  return False

            send("Are we still talking about " + t + "?  (Please answer \"yes\" or \"no\")")
            self.memory.push("status", "conv_topic")

        return None

    def conv_topic(self, mess):
        """
        Called when the user responds to Dodona's
        question of whether they are talking about
        a certain topic, and processes the users's
        answer.

        Corresponds to the status conv_topic.
        """
        name = self.name
        if mess.find("yes") != -1:
            send("Ok!", name)
            return None
        
        if mess.find("no") != -1:
            send("Duly noted.", name)
            self.memory.pop("topic")
            self.memory.pop("status")
            return False

        return None

    def clear(self):
        """
        Clears (resets) the session and the
        memory, but does not kill it.
        """
        self.memory = FuzzyStack(20)
        self.memory.push("data", topics)        

    def question(self):
        """
        Parses the user's most recent message,
        and decides what to do based on the
        content and the current status.
        """
        name = self.name
        mess = self.memory.read("message")
        m = tokenize(mess)

        if mess == None: return False

        # if the user wants to exit, then
        # return True (kill the session)
        if mess == "exit" or \
                "bye" in m or \
                "goodbye" in m:
            send("Glad to be of help :)", name)
            return True

        # if the user says "nevermind", then
        # clear the session
        if mess.find("nevermind") != -1:
            send("Ok.", name)
            self.clear()
            return False

        # if the user greets Dodona, then respond
        # in kind.
        if "hi" in m or \
                "hey" in m or \
                "hello" in m != -1:
            send("Hello, " + name + "!")
            return None
        
        # check the status, and return the corresponding
        # function if necessary
        s = self.memory.read("status")
        if s == "unknown":  return self.unknown(mess)
        if s == "conv_topic":  return self.conv_topic(mess)
        if s == "subtopic":  return self.sub_topic(mess)
        if s == "add_data_true":  return self.add_data(mess, True)
        if s == "add_data_false":  return self.add_data(mess, False)

        d = self.memory.read("data")
        k = self.memory.read("topic")
        # if there is no current topic, then decipher one
        # from the most recent message.
        if k == None:  key = self.AI(mess)
        # if there is a current topic, search for a subtopic
        else:  key = self.AI(mess, d)

        # if there is no matching key, then ask the user to
        # tell Dodona about the topic.
        if key == "d:none":
            topic = mess
            if topic.strip() == "": return None
            self.memory.push("topic", topic)
            send("Sorry, I don't know anything about " + topic + ".  Would you like to tell me about " + topic + "?  (Please answer \"yes\" or \"no\")", name)
            self.memory.push("status", "unknown")
            return None
        
        # if the key is a list, tihs means that there are
        # multiple matching keywords.  Prompt the user as to
        # which one they want.
        if isinstance(key, list):
            send("Multiple keywords match your query.  What did you mean to ask about?\n\n" + print_list(key), name)
            shortd = {}
            for item in key:
                shortd[item] = d[item]
            self.memory.push("data", shortd)
            while(self.memory.read("message") != None):
                self.memory.pop("message")
            return None

        # if the key is a dictionary, then you know it is a
        # topic, and has subtopics.  Ask the user which subtopic
        # they would like to know about.
        if isinstance(d[key], dict):
            key2 = self.AI(mess, d[key])

            if key2 == "d:none" or isinstance(key2, list):
                send("Please pick a topic below, or tell me a new one! (in relation to " + key + ")\n\n" + print_list(d[key].keys()), name)
                self.memory.push("topic", key)
                self.memory.push("data", d[key])
                return None

            else:
                send(d[key][key2], name)
                return False

        # if there is just a single key, then respond with
        # the knowledge which Dodona has about the topic
        send(custom_fill(d[key]), name)
        return False
 
# -*- indent-tabs-mode: nil; tab-width: 4; -*-
# vi: set ts=4 sw=4 et:
