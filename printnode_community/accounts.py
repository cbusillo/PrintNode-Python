class Accounts:

    def __init__(self, auth, factory):
        self._auth = auth
        self._factory = factory

    def get_clients(self, client_ids=None, os=None):
        if os:
            url = "/download/client/"+os
            clients = self._factory.create_latest_download(
                self._auth.get(url))
        else:
            client_ids = str(client_ids) if client_ids else ""
            url = "/download/clients/"+client_ids
            clients = self._factory.create_clients(self._auth.get(url))

        return clients

    def modify_client_downloads(self, client_ids, enabled):
        if not isinstance(enabled, bool):
            raise ValueError('Incorrect type of enabled, should be bool.')

        response = self._auth.patch(
            "/download/clients/"+str(client_ids),
            {"enabled": enabled})

        return response

    def get_tag(self, tagname):
        tags = self._auth.get('account/tag/'+tagname)

        return tags

    def modify_tag(self, tagname, tagvalue):
        tags = self._auth.post('account/tag/'+tagname, tagvalue)

        return tags

    def delete_tag(self, tagname):
        tags = self._auth.delete('account/tag/'+tagname)

        return tags

    def modify_account(
            self,
            firstname=None,
            lastname=None,
            password=None,
            email=None,
            creator_ref=None
            ):
        mod_data = {}
        if firstname is not None:
            mod_data.update({"firstname": firstname})
        if lastname is not None:
            mod_data.update({"lastname": lastname})
        if password is not None:
            mod_data.update({"password": password})
        if email is not None:
            mod_data.update({"email": email})
        if creator_ref is not None:
            mod_data.update({"creatorRef": creator_ref})
        if not mod_data:
            raise ValueError("No fields selected to be modified, exiting")
        account_id = self._auth.patch('/account', mod_data)
        return account_id

    def create_account(
            self,
            firstname,
            lastname,
            email,
            password,
            creator_ref=None,
            api_keys=None,
            tags=None):

        acc_data = {
                "Account": {
                    "firstname": firstname,
                    "lastname": lastname,
                    "email": email,
                    "password": password}
                }

        if creator_ref is not None:
            acc_data["Account"].update({"creatorRef": creator_ref})

        if api_keys is not None:
            acc_data.update({"ApiKeys": api_keys})

        if tags is not None:
            acc_data.update({"Tags": tags})

        acc_id = self._auth.post('/account', acc_data)

        return acc_id

    def delete_account(
            self,
            ):

        response = self._auth.delete("/account")

        return response

    def delete_api_key(
            self,
            api_key,
            ):

        response = self._auth.delete('account/apikey/'+api_key)

        return response

    def get_api_key(
            self,
            api_key
            ):

        response = self._auth.get("/account/apikey/"+api_key)
        return response

    def create_api_key(
            self,
            api_key,
            ):
        response = self._auth.post("/account/apikey/"+api_key)
        return response

    def get_clientkey(
            self,
            uuid,
            version,
            edition):
        url = "/client/key/"+uuid+"?edition="+edition+"&version="+version
        response = self._auth.get(url, {'Content-Type': 'application/json'})
        return response
