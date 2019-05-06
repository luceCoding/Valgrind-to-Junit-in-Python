# from xml.etree import ElementTree as ET
import hashlib
import base64

class ValgrindError(object):
    def __init__(self, xml_error=None):
        self.xml_error = xml_error
        self.failure_type = None
        self.failure_message = None
        self.stack = None

    def get_testcase_time(self):
        if self.xml_error is None:
            return ''
        return '0'

    def get_testcase_classname(self, classname=None):
        if self.xml_error is None:
            return ''
        if classname is None:
            return 'valgrind'
        return classname

    def get_testcase_name(self, testcase=None):
        if self.xml_error is None:
            return ''
        if testcase is None:
            return self.xml_error.find('unique').text
        hash_str = self.get_hash(testcase)
        return ' '.join([self.get_failure_type(), hash_str])

    def get_failure_type(self): # kind tag in valgrind
        if self.failure_type is not None:
            return self.failure_type
        if self.xml_error is None:
            return ''
        self.failure_type = self.xml_error.find('kind').text
        return self.failure_type

    def get_failure_message(self): # what tag in valgrind
        if self.failure_message is not None:
            return self.failure_message
        if self.xml_error is None:
            return ''
        self.failure_message = self.xml_error.find('what').text
        return self.failure_message

    def get_failure_details(self): # stack tag in valgrind
        if self.stack is not None:
            return self.stack
        if self.xml_error is None:
            return ''
        stack = self.xml_error.find('stack')
        self.stack = ' '.join(x.text for x in stack.iter())
        return self.stack

    def remove_tags(self, tag_to_remove):
        if self.xml_error is None:
            return False
        tags_to_remove = list()
        for tag in self.xml_error.iter(tag_to_remove):
            tags_to_remove.append(tag)
        for tag in tags_to_remove:
            parent = tag.getparent()
            parent.remove(tag)
        return True if len(tags_to_remove) else False

    def get_hash(self, input=''):
        self.remove_tags('ip')
        kind_str = self.get_failure_type()
        what_str = self.get_failure_message()
        stack_str = self.get_failure_details()
        str_to_hash = input + kind_str + what_str + stack_str
        md5_str = hashlib.md5(str_to_hash.encode('utf-8')).digest()
        base64_str = base64.b64encode(md5_str)
        return str(base64_str)[2:-1]