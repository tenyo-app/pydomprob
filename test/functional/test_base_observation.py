from domprob import announcement, BaseObservation


class MockObservationOne(BaseObservation):
    pass


class MockObservationTwo(BaseObservation):
    @announcement(...)
    def mock_announcement_one(self): ...

    @announcement(...)
    def mock_announcement_two(self): ...


class MockObservationThree(BaseObservation):
    @announcement(...)
    @announcement(...)
    @announcement(...)
    def mock_announcement_one(self): ...

    @announcement(...)
    def mock_announcement_two(self): ...


class TestBaseObservation:

    def test_no_announcements(self):
        # Arrange
        obs = MockObservationOne()
        # Act
        inst_announcements = list(obs.announcements())
        cls_announcements = list(MockObservationOne.announcements())
        # Assert
        assert len(inst_announcements) == 0
        assert len(cls_announcements) == 0
        assert inst_announcements == cls_announcements
        assert len(obs) == 0

    def test_simple_announcements(self):
        # Arrange
        obs = MockObservationTwo()
        # Act
        inst_announcements = list(obs.announcements())
        cls_announcements = list(MockObservationTwo.announcements())
        # Assert
        assert len(inst_announcements) == 2
        assert len(cls_announcements) == 2
        assert inst_announcements == cls_announcements
        assert len(obs) == 2

    def test_stacked_announcements(self):
        # Arrange
        obs = MockObservationThree()
        # Act
        inst_announcements = list(obs.announcements())
        cls_announcements = list(MockObservationThree.announcements())
        # Assert
        assert len(inst_announcements) == 2
        assert len(cls_announcements) == 2
        assert inst_announcements == cls_announcements
        assert len(obs) == 2
