第一步
https://centerapi.qschou.com/passport/sms/login

{
    "country_code": "CN",
    "phone": "18226287291",
    "sms_code": "9527",
    "auth_key": "qsevidence_pc"
}

{
    "code": 0,
    "msg": "",
    "data": {
        "access_token": "",
        "refresh_token": "",
        "token_type": "",
        "expires_in": "0",
        "srv_create_time": "0",
        "user_list": [
            {
                "avatar_thumb": "https://thumb.qschou.com/files/qschou.com/avatar/517/e68aa629-0b43-11ee-aeac-0242ac11f012/e6a375a0-0b43-11ee-aeac-0242ac11f012.jpeg@!thumb.png",
                "nickname": "抱朴",
                "user_id": "534332517",
                "random_num": "af5ZELDT677309"
            },
            {
                "avatar_thumb": "https://thumb.qschou.com/files/qschou.com/avatar/825/8e6006be-2d57-11eb-9f11-0242ac11400d/d9f96b32-2d57-11eb-9f11-0242ac11400d.jpeg@!thumb.png",
                "nickname": "抱朴",
                "user_id": "151565110",
                "random_num": "9S3K1rBT1eb566"
            }
        ]
    },
    "next": ""
}



第二步
https://centerapi.qschou.com/passport/phone-multi-user
{
    "random_num": "af5ZELDT677309"
}


{
    "code": 0,
    "msg": "",
    "data": {
        "access_token": "5da49254021c2a0be921bf4d1d6e319103b8e039",
        "refresh_token": "e34f114f5498bc6ec4b3f7f8d8fe97b118a7ed7b",
        "token_type": "Bearer",
        "expires_in": "4200",
        "srv_create_time": "1761565123"
    },
    "next": ""
}

获取access_token 为token