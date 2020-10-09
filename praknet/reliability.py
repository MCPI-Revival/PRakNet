unreliable = 0
unreliable_sequenced = 1
reliable = 2
reliable_ordered = 3
reliable_sequenced = 4
unreliable_ack_receipt = 5
reliable_ack_receipt = 6
reliable_ordered_ack_receipt = 7

@staticmethod
def is_reliable(reliability):
    if reliability == reliable:
        return True
    elif reliability == reliable_ordered:
        return True
    elif reliability == reliable_sequenced:
        return True
    elif reliability == reliable_ack_receipt:
        return True
    elif reliability == reliable_ordered_ack_receipt:
        return True
    else:
        return False
        
@staticmethod
def isSequenced(reliability):
        if reliability == unreliable_sequenced:
            return True
        elif reliability == reliable_sequenced:
            return True
        else:
            return False

@staticmethod
def is_ordered(reliability):
    if reliability == reliable_ordered:
        return True
    elif reliability == reliable_ordered_ack_receipt:
        return True
    else:
        return False

@staticmethod
def is_sequenced_or_ordered(reliability):
    if reliability == unreliable_sequenced:
        return True
    elif reliability == reliable_ordered:
        return True
    elif reliability == reliable_sequenced:
        return True
    elif reliability == reliable_ordered_ack_receipt:
        return True
    else:
        return False
