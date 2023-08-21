from datetime import datetime
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce


class Budget(models.Model):

    related_name = 'budgets'

    # A tuple of tuples, containing the short name and full name of each month.
    MONTH_CHOICES = (
        ('JAN', 'January'), ('FEB', 'February'), ('MAR', 'March'),
        ('APR', 'April'), ('MAY', 'May'), ('JUN', 'June'),
        ('JUL', 'July'), ('AUG', 'August'), ('SEP', 'September'),
        ('OCT', 'October'), ('NOV', 'November'), ('DEC', 'December')
    )

    # A dictionary, mapping the month's short name to its index in MONTH_CHOICES.
    MONTH_LOOKUP = {choice[0]: index for index, choice in enumerate(MONTH_CHOICES)}

    month = models.CharField(max_length=100, choices=MONTH_CHOICES, default='JAN')
    year = models.IntegerField(default=datetime.now().year)
    owner = models.ForeignKey('auth.User', related_name=related_name, on_delete=models.CASCADE)

    # This method calculates the previous month's index and year, considering a wrap-around 
    # from January to December.
    @staticmethod
    def get_previous_month(month_idx, year):
        """
        input: month_idx (index of the current month) and year.
        Output: The index of the previous month and the corresponding year.
        """
        # Subtracting 1 from month_idx
        month_idx -= 1 
        # When month_idx is less than 0, it sets month_idx to 11 (representing December) and decrements the year by 1. 
        if month_idx < 0: 
            month_idx = 11
            year -= 1
        return month_idx, year
    
    # This property returns the previous month's budget for the same owner if it exists. 
    @property
    def previous(self):
        # it uses the get_previous_month method to find the previous month and then queries the database.
        month_idx, year = self.get_previous_month(self.MONTH_LOOKUP[self.month], self.year)
        try:
            return Budget.objects.get(owner=self.owner, year=year, month=self.MONTH_CHOICES[month_idx][0])
        except Budget.DoesNotExist:
            return None
    class Meta:
        # unique_together: Ensures that there is only one budget for each combination of owner, month, and year.
        unique_together = ('owner', 'month', 'year') 

    def __str__(self):
        return f"{self.owner.username}'s {self.month} {self.year} Budget"
    
class BudgetCategoryGroup(models.Model):
    """
    The BudgetCategoryGroup class represents a grouping of budget categories within the budgeting system. 
    Grouping categories allows users to organize different budget categories under common headings, 
    such as "Living Expenses" or "Entertainment." This class forms a hierarchical structure in the budgeting
    system where a budget category group contains multiple budget categories
    """
    related_name = 'budget_category_groups'
    name = models.CharField(max_length=100)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name=related_name)

    @property
    def owner(self):
        return self.budget.owner

    class Meta:
        unique_together = ('name', 'budget',)

    def __str__(self):
        return f"{self.name} [owner={self.budget.owner.username}]"

class BudgetCategory(models.Model):
    related_name = 'budget_categories'
    category = models.CharField(max_length=100)
    group = models.ForeignKey(
        BudgetCategoryGroup,
        on_delete=models.CASCADE,
        related_name=related_name
    )
    limit = models.DecimalField(
        max_digits=20, decimal_places=2, default=0
    )
    # The spent property within the BudgetCategory class calculates the total amount spent within a specific budget category. 
    @property
    def spent(self):
        return Decimal(
            Transaction.objects
            .filter(budget_category_id=self.pk)
            .aggregate(spent=Coalesce(Sum('amount'), Decimal(0)))['spent']
        )

    def __str__(self):
        return f"{self.category} {self.group.budget.month} {self.group.budget.year} [owner={self.group.budget.owner.username}]"


class Transaction(models.Model):
    """
    The Transaction class represents a financial transaction within the budgeting system.
    """
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    payee = models.ForeignKey('Payee', on_delete=models.CASCADE)
    budget_category = models.ForeignKey('BudgetCategory', on_delete=models.CASCADE)
    date = models.DateField()
    
    # This property provides a convenient way to access the owner of the transaction.
    @property
    def owner(self):
        return self.budget_category.group.budget.owner

    def __str__(self):
        return f"{self.amount} {self.payee.name} {self.budget_category} {self.date} {self.budget_category.group.budget.owner.username}"


class Payee(models.Model):
    """
    The Payee class represents a person or entity to whom a payment is made. 
    It's a simple model within the budgeting system but plays a vital role in linking transactions 
    to specific recipients. 
    """
    name = models.CharField(max_length=30)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'owner',)

    def __str__(self):
        return self.name



