class AppState:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.current_user = None
        self.current_household = None
        self.household_members = []

# because this is memory only, when the app closes, the data is lost. Later can improve this with local storage.