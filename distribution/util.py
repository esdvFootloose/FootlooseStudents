from django.utils.safestring import mark_safe

def create_couple_block(couple):
    leader = couple.leader
    follower = couple.follower
    status = couple.get_highest_status()
    if status == 'student':
        status_text = 'S'
    elif status == 'student_eindhoven':
        status_text = 'E|S'
    elif status == 'active_member':
        status_text = 'A'

    else:
        status_text = "-"

    if hasattr(couple.leader, 'verifytoken'):
        leader = "<div style=\"color:red;\">{}</div>".format(leader)
    else:
        leader = "<div>{}</div>".format(leader)
    if hasattr(couple.follower, 'verifytoken'):
        follower = "<div style=\"color:red;\">{}</div>".format(follower)
    else:
        follower = "<div>{}</div>".format(follower)
    return mark_safe(
        "<li class=\"member\" data-couple-id=\"{}\">"
        "{} {}<button class=\"button secondary\">{}</button><button class='button alert' onclick='delete_couple_block(this);'>Delete</button>"
        "</li>".format(couple.pk, leader, follower, status_text)
    )