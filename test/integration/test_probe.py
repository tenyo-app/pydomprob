class TestProbeImports:
    def test_get_probe(self):
        # Arrange
        from domprob import get_probe as alias_get_probe
        from domprob.probes.probe import get_probe

        # Act
        # Assert
        assert alias_get_probe is get_probe

    def test_probe(self):
        # Arrange
        from domprob import probe as alias_probe
        from domprob.probes.probe import probe

        # Act
        # Assert
        assert alias_probe is probe

    def test_probe_cls(self):
        # Arrange
        from domprob import Probe as AliasProbe
        from domprob.probes.probe import Probe

        # Act
        # Assert
        assert AliasProbe is Probe
