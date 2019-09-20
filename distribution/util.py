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
        "<li class=\"member\" data-couple-id=\"{}\">"
        "{}<br/>{}<br/>{}<br/><a class='button alert' onclick='delete_couple_block(this);'>delete<a/>"
        "</li>".format(couple.pk, leader, follower, status)
    )