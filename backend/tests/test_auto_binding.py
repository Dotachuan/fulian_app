import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.crud.member import auto_bind_member_by_name
from app.db.database import Base
from app.models.donor import Donor
from app.models.member import Member
from app.models.member_binding_request import MemberBindingRequest


class AutoBindingTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.member = Member(
            phone="13800138000",
            status="active",
            binding_status="unbound",
            binding_source="auto",
        )
        self.db.add(self.member)
        self.db.commit()
        self.db.refresh(self.member)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def add_donor(self, name: str, phone: str | None = None) -> Donor:
        donor = Donor(name=name, type="person", phone=phone, is_deleted=False)
        self.db.add(donor)
        self.db.commit()
        self.db.refresh(donor)
        return donor

    def test_unique_name_is_bound_automatically(self):
        donor = self.add_donor("张三")

        result = auto_bind_member_by_name(self.db, self.member, "张 三", self.member.phone)

        self.assertEqual(result["result"], "bound")
        self.assertEqual(self.member.donor_id, donor.id)
        self.assertEqual(donor.binding_bound_member_id, self.member.id)
        self.assertEqual(donor.phone, self.member.phone)

    def test_missing_name_requires_confirmation_before_creation(self):
        result = auto_bind_member_by_name(self.db, self.member, "李四", self.member.phone)

        self.assertEqual(result["result"], "confirm_create")
        self.assertEqual(self.db.query(Donor).count(), 0)
        self.assertIsNone(self.member.donor_id)

    def test_confirmed_missing_name_creates_and_binds_donor(self):
        result = auto_bind_member_by_name(
            self.db,
            self.member,
            "李四",
            self.member.phone,
            confirm_create=True,
        )

        donor = self.db.query(Donor).one()
        self.assertEqual(result["result"], "bound")
        self.assertEqual(donor.name, "李四")
        self.assertEqual(self.member.donor_id, donor.id)

    def test_duplicate_names_are_sent_to_manual_review(self):
        self.add_donor("王五")
        self.add_donor("王五")

        result = auto_bind_member_by_name(self.db, self.member, "王五", self.member.phone)

        request = self.db.query(MemberBindingRequest).one()
        self.assertEqual(result["result"], "manual_review")
        self.assertEqual(self.member.binding_status, "ambiguous")
        self.assertEqual(request.status, "pending")

    def test_phone_conflict_is_sent_to_manual_review(self):
        self.add_donor("赵六", "13900139000")

        result = auto_bind_member_by_name(self.db, self.member, "赵六", self.member.phone)

        self.assertEqual(result["result"], "manual_review")
        self.assertEqual(self.member.binding_status, "ambiguous")
        self.assertIsNone(self.member.donor_id)


if __name__ == "__main__":
    unittest.main()
