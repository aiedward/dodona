import site
site.addsitedir('/afs/athena.mit.edu/user/b/r/broder/lib/python2.5/site-packages')
from xml.dom import minidom

def load_topics(file):
    """
    Loads the topics from the specified file,
    and parse the XML to find the file which
    each topic is associated with.  Returns a
    dictionary of the topics and their associated
    infomation.
    """
    topics = {}
    xmldoc = minidom.parse(file)
    topicsNode = xmldoc.firstChild
    for topic in topicsNode.childNodes:
        if topic.nodeType == topic.ELEMENT_NODE and topic.localName == "topic":
            topic_name = topic.attributes["name"].value.lower()
            topic_file = topic.attributes["file"].value
            topics[topic_name.encode('ascii')] = load_topic(topic_file)
    for topic in topicsNode.childNodes:
        if topic.nodeType == topic.ELEMENT_NODE and topic.localName == "alias":
            topic_name = topic.attributes["name"].value.lower()
            topic_file = topic.attributes["to"].value
            topics[topic_name.encode('ascii')] = topics[(topic_file)]

    print topics.keys()
    return topics

def load_topic(file):
    """
    Load the information about a topic from
    the specified file, and return a dictionary
    with said information.
    """
    answers = {}
    print "Loading " + file + "..."
    xmldoc = minidom.parse(file)
    topicNode = xmldoc.firstChild
    for answer in topicNode.childNodes:
        if answer.nodeType == answer.ELEMENT_NODE:
            if answer.localName == "answer":
                answer_question = answer.attributes["question"].value.lower()
                answers[answer_question.encode('ascii')] = answer.firstChild.data
            elif answer.localName == "default":
                default_answer = answer.firstChild.data
                answers["default"] = default_answer
    return answers

def update_files(topic, topics, newtopic=True):
    """
    Updates the XML files with new information, which
    is added by users.
    """
    file = open("./doctopics/" + topic + ".xml", "w")
    file.write("<?xml version=\"1.0\" ?>\n")
    file.write("<topic>\n")
    file.write("<default>Overview of " + topic + "</default>\n")
    
    for subtopic in topics[topic]:
        file.write("<answer question=\"" + subtopic + "\">\n")
        file.write(topics[topic][subtopic] + "\n")
        file.write("</answer>\n")
    
    file.write("</topic>")
    file.close()

    if newtopic:
        file = open("./doctopics/topics.xml", "r")
        f = []
        line = None
        while line != "":
            line = file.readline()
            if line.find("</topics>") == -1:
                f.append(line)
            else:
                f.append("<topic name=\"" + topic + "\" file=\"doctopics/" + topic + ".xml\"/>\n")
                f.append(line)

        file.close()
        file = open("./doctopics/topics.xml", "w")
        for line in f:
            file.write(line)

        file.close() 
