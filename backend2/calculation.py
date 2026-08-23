# ==========================================
# DineMapAI - Location Scoring Model
# ==========================================


# ---------- WEIGHTS ----------

WEIGHTS = {
    "demand": 0.30,
    "competition": 0.20,
    "accessibility": 0.20,
    "audience": 0.15,
    "time": 0.10,
    "weather": 0.05
}


# ==========================================
# NORMALIZATION
# ==========================================

def normalize(value, minimum, maximum):

    if maximum == minimum:
        return 50

    return (
        (value - minimum)
        / (maximum - minimum)
    ) * 100


# ==========================================
# DEMAND
# ==========================================

def calculate_demand(data):

    college_score = normalize(
        data["colleges"],
        0,
        20
    )

    university_score = normalize(
        data["universities"],
        0,
        10
    )

    office_score = normalize(
        data["offices"],
        0,
        100
    )

    mall_score = normalize(
        data["malls"],
        0,
        10
    )


    demand = (

        college_score * 0.40

        + university_score * 0.30

        + office_score * 0.20

        + mall_score * 0.10
    )


    return demand


# ==========================================
# COMPETITION
# ==========================================

def calculate_competition(data):

    cafe_pressure = normalize(
        data["cafes"],
        0,
        30
    )

    restaurant_pressure = normalize(
        data["restaurants"],
        0,
        100
    )


    competition_pressure = (

        cafe_pressure * 0.70

        + restaurant_pressure * 0.30
    )


    # More competition = lower opportunity

    competition_score = (
        100 - competition_pressure
    )


    return competition_score


# ==========================================
# ACCESSIBILITY
# ==========================================

def distance_score(distance):

    if distance <= 0.25:
        return 100

    elif distance <= 0.5:
        return 90

    elif distance <= 1:
        return 75

    elif distance <= 2:
        return 50

    elif distance <= 3:
        return 30

    else:
        return 10


def calculate_accessibility(data):

    metro = distance_score(
        data["metro_distance"]
    )

    bus = distance_score(
        data["bus_distance"]
    )

    train = distance_score(
        data["train_distance"]
    )


    accessibility = (

        metro * 0.45

        + bus * 0.35

        + train * 0.20
    )


    return accessibility


# ==========================================
# TARGET AUDIENCE
# ==========================================

def calculate_audience_fit(
    data,
    audience
):

    if audience == "student":

        college = normalize(
            data["colleges"],
            0,
            20
        )

        university = normalize(
            data["universities"],
            0,
            10
        )


        return (

            college * 0.55

            + university * 0.45
        )


    elif audience == "office_worker":

        office = normalize(
            data["offices"],
            0,
            100
        )

        return office


    elif audience == "general":

        return calculate_demand(data)


    else:

        return 50


# ==========================================
# TIME OF DAY
# ==========================================

def calculate_time_score(
    data,
    audience,
    time_of_day
):

    if audience == "student":

        scores = {

            "morning": 65,

            "afternoon": 85,

            "evening": 90,

            "night": 60
        }


    elif audience == "office_worker":

        scores = {

            "morning": 80,

            "afternoon": 95,

            "evening": 85,

            "night": 40
        }


    else:

        scores = {

            "morning": 70,

            "afternoon": 80,

            "evening": 85,

            "night": 60
        }


    return scores.get(
        time_of_day,
        50
    )


# ==========================================
# FINAL SCORE
# ==========================================

def calculate_final_score(
    demand,
    competition,
    accessibility,
    audience,
    time,
    weather
):

    score = (

        demand
        * WEIGHTS["demand"]

        + competition
        * WEIGHTS["competition"]

        + accessibility
        * WEIGHTS["accessibility"]

        + audience
        * WEIGHTS["audience"]

        + time
        * WEIGHTS["time"]

        + weather
        * WEIGHTS["weather"]
    )


    return round(score, 2)