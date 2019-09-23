from django.utils.safestring import mark_safe

def create_couple_block(couple):
    leader = couple.leader
    follower = couple.follower
    status = couple.get_highest_status()
    if status is not None:
        status = status[0].upper()
    else:
        status = "-"

    if hasattr(couple.leader, 'verifytoken'):
        leader = "<div style=\"color:red;\">{}</div>".format(leader)
    if hasattr(couple.follower, 'verifytoken'):
        follower = "<div style=\"color:red;\">{}</div>".format(follower)
    return mark_safe(
        "<li class=\"member\" data-couple-id=\"{}\">"
        "{} {}<button class=\"button secondary\">{}</button><button class='button alert' onclick='delete_couple_block(this);'>Delete</button>"
        "</li>".format(couple.pk, leader, follower, status)
    )