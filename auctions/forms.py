from django import forms


class NewListingForm(forms.Form):
    title = forms.CharField(label="title")
    description = forms.CharField(label="description")
    starting_bid = forms.CharField(label="starting_bid")
    image = forms.CharField(label="image", required=False)
    category = forms.CharField(label="category", required=False)
