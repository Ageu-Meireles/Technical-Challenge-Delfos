import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import pandas as pd

from src.main import parse_date, fetch_source_data, aggregate_data, ensure_signals, load_data, run_etl


class TestParseDate:
    def test_parse_date_valid(self):
        result = parse_date("2024-01-15")
        assert result == datetime(2024, 1, 15)

    def test_parse_date_invalid(self):
        with pytest.raises(ValueError):
            parse_date("15-01-2024")


class TestFetchSourceData:
    @patch('src.main.httpx.Client')
    @patch('src.main.settings')
    def test_fetch_source_data_success(self, mock_settings, mock_client_class):
        mock_settings.source_api_url = "http://test.com"
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = [
            {"timestamp": "2024-01-15T10:00:00", "wind_speed": 10.5, "power": 100.0}
        ]
        mock_client.get.return_value = mock_response
        
        date = datetime(2024, 1, 15)
        result = fetch_source_data(date, client=mock_client)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch('src.main.httpx.Client')
    @patch('src.main.settings')
    def test_fetch_source_data_empty(self, mock_settings, mock_client_class):
        mock_settings.source_api_url = "http://test.com"
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_client.get.return_value = mock_response
        
        date = datetime(2024, 1, 15)
        
        with pytest.raises(RuntimeError):
            fetch_source_data(date, client=mock_client)


class TestAggregateData:
    def test_aggregate_data(self):
        timestamps = pd.date_range("2024-01-15 10:00:00", periods=4, freq="5min")
        df = pd.DataFrame({
            "wind_speed": [10.0, 11.0, 12.0, 13.0],
            "power": [100.0, 105.0, 110.0, 115.0]
        }, index=timestamps)
        
        result = aggregate_data(df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # 4 records resampled to 10min

    def test_aggregate_data_empty(self):
        df = pd.DataFrame()
        with pytest.raises(TypeError):
            aggregate_data(df)


class TestEnsureSignals:
    def test_ensure_signals_new(self, mock_session):
        mock_session.exec.return_value.all.return_value = []
        
        result = ensure_signals(mock_session)
        
        assert len(result) == 8  # 2 variables * 4 aggregations
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    def test_ensure_signals_existing(self, mock_session):
        from src.db.models import Signal
        existing_signals = [
            Signal(id=1, name="wind_speed_mean"),
            Signal(id=2, name="wind_speed_min"),
            Signal(id=3, name="wind_speed_max"),
            Signal(id=4, name="wind_speed_std"),
            Signal(id=5, name="power_mean"),
            Signal(id=6, name="power_min"),
            Signal(id=7, name="power_max"),
            Signal(id=8, name="power_std"),
        ]
        mock_session.exec.return_value.all.return_value = existing_signals
        
        result = ensure_signals(mock_session)
        
        assert len(result) == 8
        mock_session.add.assert_not_called()


class TestLoadData:
    def test_load_data_new_records(self, mock_session):
        timestamps = pd.date_range("2024-01-15 10:00:00", periods=2, freq="10min")
        aggregated = pd.DataFrame({
            "wind_speed_mean": [10.5, 11.5]
        }, index=timestamps)
        
        signal_map = {"wind_speed_mean": 1}
        mock_session.exec.return_value.first.return_value = None
        
        load_data(mock_session, aggregated, signal_map)
        
        mock_session.bulk_save_objects.assert_called()
        mock_session.commit.assert_called()

    def test_load_data_skip_existing(self, mock_session):
        timestamps = pd.date_range("2024-01-15 10:00:00", periods=1, freq="10min")
        aggregated = pd.DataFrame({
            "wind_speed_mean": [10.5]
        }, index=timestamps)
        
        signal_map = {"wind_speed_mean": 1}
        existing_data = Mock()
        mock_session.exec.return_value.first.return_value = existing_data
        
        load_data(mock_session, aggregated, signal_map)
        
        mock_session.bulk_save_objects.assert_not_called()


class TestRunETL:
    @patch('src.main.load_data')
    @patch('src.main.ensure_signals')
    @patch('src.main.aggregate_data')
    @patch('src.main.fetch_source_data')
    @patch('src.main.parse_date')
    @patch('src.main.Session')
    def test_run_etl_success(self, mock_session_class, mock_parse_date, 
                           mock_fetch, mock_aggregate, mock_ensure_signals, mock_load_data):
        mock_parse_date.return_value = datetime(2024, 1, 15)
        mock_fetch.return_value = pd.DataFrame({"wind_speed": [10.0]})
        mock_aggregate.return_value = pd.DataFrame({"wind_speed_mean": [10.5]})
        
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_ensure_signals.return_value = {"wind_speed_mean": 1}
        
        run_etl("2024-01-15")
        
        mock_parse_date.assert_called_once_with("2024-01-15")
        mock_fetch.assert_called_once()
        mock_aggregate.assert_called_once()
        mock_ensure_signals.assert_called_once()
        mock_load_data.assert_called_once()


@pytest.fixture
def mock_session():
    session = Mock()
    session.exec = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    session.bulk_save_objects = Mock()
    return session
