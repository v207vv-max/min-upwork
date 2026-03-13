def user_is_client(user):
    return bool(user and user.is_authenticated and getattr(user, "is_client", False))


def user_is_freelancer(user):
    return bool(user and user.is_authenticated and getattr(user, "is_freelancer", False))


def user_can_view_bid(user, bid):
    if not user or not user.is_authenticated:
        return False

    return bid.freelancer == user or bid.project.client == user


def user_can_manage_bid(user, bid):
    if not user or not user.is_authenticated:
        return False

    return bid.freelancer == user and bid.is_editable


def user_can_view_contract(user, contract):
    if not user or not user.is_authenticated:
        return False

    return contract.client == user or contract.freelancer == user


def user_can_manage_contract(user, contract):
    if not user or not user.is_authenticated:
        return False

    return contract.client == user and contract.is_active


def user_can_view_review(user, review):
    if not user or not user.is_authenticated:
        return False

    return review.client == user or review.freelancer == user


def user_can_manage_review(user, review):
    if not user or not user.is_authenticated:
        return False

    return review.client == user