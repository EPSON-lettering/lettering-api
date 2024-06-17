class CommonInterest:

    def __init__(self, patt, matt):
        self.patt_interests = patt
        self.matt_interests = matt

    def calculate(self):
        patt = set(self.patt_interests)
        dup = []
        for item in self.matt_interests:
            for patt_item in patt:
                # print(f'matt_item: {item}, patt_item: {patt_item}')
                if item == patt_item:
                    dup.append(item)

        return dup
