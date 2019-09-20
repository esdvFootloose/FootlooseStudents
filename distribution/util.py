from django.utils.safestring import mark_safe

def create_couple_block(couple):
    leader = couple.leader
    follower = couple.follower
    status = couple.get_highest_status()
    if status is not None:
        status = status[0].upper()
    else:
        status = "-"
    return mark_safe(
        "<li class=\"member\" couple-id=\"{}\">{}<br/>{}<br/>{}</li>".format(couple.pk, leader, follower, status)
    )