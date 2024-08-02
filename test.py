from backend.database import get_db
from backend.models.pool import Pool
import backend.models.payout as payout

db = next(get_db())

print(payout.get_user_payouts(2023))

