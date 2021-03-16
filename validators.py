VALID_USER_UPDATE_FIELDS = ['name', 'picture', 'company', 'email', 'phone', 'skills']


# Helpers
class ValidatorResponse:
    def __init__(self, success, message=None):
        self.success = success
        self.message = message


def check_int(val):
    try:
        int(val)
        return True
    except TypeError:
        return False


def check_int_or_none(val):
    if not check_int(val):
        return val is None
    else:
        return True


def generate_failed_validator_response(failed_validators):
    return [{'valid_request': validator.success, 'message': validator.message} for validator in failed_validators]


def check_validators(validator_responses):
    failed_validators = list(filter(lambda validator: not validator.success if validator is not None else None,
                                    validator_responses))

    return generate_failed_validator_response(failed_validators) if len(failed_validators) > 0 else []


# Validators
def validate_request_parameters(request, valid_parameters):
    if set(request.args.keys()).issubset(valid_parameters):
        return ValidatorResponse(True)
    return ValidatorResponse(False, f"Invalid Parameter(s), valid parameter(s) are: {','.join(valid_parameters)}")


def validate_user_request(request, cur):
    if request.args.get('user') is not None:
        if request.args.get('user').find(',') != -1:
            return ValidatorResponse(False, "Cannot pass multiple parameters with 'x,y'. Instead, use ?param=x&param=y")
        cur.execute("SELECT id FROM users")
        valid_ids = set(map(lambda row: f'{row[0]}', cur.fetchall()))
        if not set(request.args.getlist('user')).issubset(valid_ids):
            return ValidatorResponse(False, f"Invalid user id")
    return ValidatorResponse(True)


def _validate_user_update_payload(user_payload):
    if len(set(user_payload.keys())) != len(user_payload.keys()):
        return ValidatorResponse(False, "Cannot pass multiple values per key for a user")

    elif set(user_payload.keys()).issubset(VALID_USER_UPDATE_FIELDS):
        return ValidatorResponse(True)

    else:
        return ValidatorResponse(False,
                                 f"Invalid keys for user update, valid keys are: {','.join(VALID_USER_UPDATE_FIELDS)}")


def validate_user_update_request(request):
    if len(request.args.getlist('user')) == 1 and isinstance(request.get_json(), dict):
        return [_validate_user_update_payload(request.get_json())]

    elif isinstance(request.get_json(), list):
        if len(request.args.getlist('user')) != len(request.get_json()):
            return [
                ValidatorResponse(False, "Number of user ids and number of entries passed for update must be equal")]
        else:
            validated_payloads = list(map(_validate_user_update_payload, request.get_json()))
            failed_paylods = list(filter(lambda validator: not validator.success, validated_payloads))
            return failed_paylods if len(failed_paylods) > 0 else [ValidatorResponse(True)]
    else:
        return [ValidatorResponse(False,
                                  "Invalid request body, must pass a JSON for single-user update, list for multi-user "
                                  "update")]


def validate_skill_request(request):
    min_frequency = request.args.get('min_frequency')
    max_frequency = request.args.get('max_frequency')

    if not check_int_or_none(min_frequency):
        return ValidatorResponse(False, "minimuim frequency must be an integer")
    elif not check_int_or_none(max_frequency):
        return ValidatorResponse(False, "maximum frequency must be an integer")
    elif check_int(min_frequency) and check_int(max_frequency):
        if int(min_frequency) > int(max_frequency):
            return ValidatorResponse(False, "minimum frequency must be less than maximum frequency")
    else:
        return ValidatorResponse(True)
