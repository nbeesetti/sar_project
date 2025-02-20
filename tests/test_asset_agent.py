import pytest
from sar_project.agents.assetmanager_agent import AssetManagerAgent

class TestAssetManagerAgent:
    @pytest.fixture
    def agent(self):
        return AssetManagerAgent()

    def test_initialization(self, agent):
        assert agent.name == "asset_manager"
        assert agent.role == "Asset Manager"
        assert agent.mission_status == "standby"
        assert agent.status == "active"
    
    def test_status_update(self, agent):
        response = agent.update_status("inactive")
        assert response["new_status"] == "inactive"
        assert agent.get_status() == "inactive"
        agent.update_status("active")

    def test_populate_kb(self, agent):
        assert len(agent.kb.assets_by_id) == 4
        assert len(agent.kb.ids_by_name) == 4
        assert len(agent.kb.get_all_assets()) == 4
        
    def test_request_get_all_assets(self, agent):
        output = agent.process_request({"message_type": "get_all_assets"})
        assets = output["all_assets"]
        assert len(assets) == 4
        assert "Drone" in str(assets)
        assert "Helicopter" in str(assets)
        assert "Rescue Boat" in str(assets)
        assert "Medical Kit" in str(assets)
    
    def test_request_find_asset_by_name(self, agent):
        output = agent.process_request({"message_type": "find_asset_id", "name": "Drone"})
        assert output["asset_id"] == "A001"
        output = agent.process_request({"message_type": "find_asset_id", "name": "Recue Boat"})
        assert output["error"] == "Asset not found"
        output = agent.process_request({"message_type": "find_asset_id", "name": "Medical Kit"})
        assert output["asset_id"] == "M010"
    
    def test_request_add_asset(self, agent):
        output = agent.process_request({"message_type": "add_asset", 
                                        "asset": {"id": "G001", 
                                                  "name": "Flashlight", 
                                                  "types": {"Tool", "Light", "Ground"}, 
                                                  "quantity": 2, 
                                                  "location_name": "SAR Base"}
                                        })
        assert output["success"] == True
        assert "Flashlight" in str(agent.kb.get_all_assets())

        output = agent.process_request({"message_type": "add_asset", "asset": {"name": "Medical Kit", "types": {"First Aid", "Medical"}, "quantity": 10, "location_name": "SAR Base"}})
        assert output["success"] == False

    def test_request_update_asset(self, agent):
        output = agent.process_request({"message_type": "update_asset", "update_field": "quantity", "id": "A001", "quantity": 2})
        assert output["success"] == True
        assert agent.kb.get_asset("A001").quantity == 7 # no replace, so 5 + 2 = 7
    
        output = agent.process_request({"message_type": "update_asset", "update_field": "quantity", "id": "A001", "quantity": 6, "replace": True})
        assert output["success"] == True
        assert agent.kb.get_asset("A001").quantity == 6 

        output = agent.process_request({"message_type": "update_asset", "update_field": "types", "name": "Drone", "types": {"Surveillance"}, "replace": False})
        assert "Surveillance" in agent.kb.get_asset("A001").types
        assert len(agent.kb.get_asset("A001").types) == 4

        output = agent.process_request({"message_type": "update_asset", "update_field": "location", "name": "Drone", "location": "Donner Pass"})
        assert agent.kb.get_asset("A001").location_name == "Donner Pass"

        output = agent.process_request({"message_type": "update_asset", "update_field": "location", "name": "Drone", "location": (39.21, -120.425)})
        assert agent.kb.get_asset("A001").location_GPS == (39.21, -120.425)

    def test_request_remove_asset(self, agent):
        agent.process_request({"message_type": "add_asset", 
                                        "asset": {"id": "G002", 
                                                  "name": "Binoculars", 
                                                  "types": {"Tool", "Ground"}, 
                                                  "quantity": 2, 
                                                  "location_name": "SAR Base"}
                                        })
        
        # print(agent.kb.get_all_assets())

        output = agent.process_request({"message_type": "remove_asset", "id": "G002"})
        # print(output)
        assert output["success"] == True
        assert "Binoculars" not in str(agent.kb.get_all_assets())

        # print(agent.kb.get_all_assets())

        output = agent.process_request({"message_type": "remove_asset", "id": "G002"})
        # print(output)
        assert output["success"] == False
        assert output["error"] == "Asset ID not found"

        output = agent.process_request({"message_type": "remove_asset", "name": "Binoculars"})
        # print(output)
        assert output["success"] == False
        assert output["error"] == "Asset not found"

    def test_request_allocate(self, agent):
        # temporary asset for testing
        agent.process_request({"message_type": "add_asset", 
                                        "asset": {"id": "G003", 
                                                  "name": "Sticks", 
                                                  "types": {"Tool", "Ground"}, 
                                                  "quantity": 6, 
                                                  "location_name": "SAR Base"}
                                        })
        
        output = agent.process_request({"message_type": "allocate", "asset_id": "G003", "team_id": "GroundTroop1", "quantity": 2})
        assert output["success"] == True
        assert agent.kb.get_asset("G003").quantity == 6
        assert agent.kb.get_asset("G003").unallocated_quantity == 4

        output = agent.process_request({"message_type": "allocate", "asset_id": "G003", "team_id": "GroundTroop1", "quantity": 10})
        assert output["success"] == False
        assert output["error"] == "Not enough units available, 4 units remaining"

        agent.process_request({"message_type": "remove_asset", "id": "G003"})
    
    def test_request_return(self, agent):
        # temporary asset for testing
        agent.process_request({"message_type": "add_asset", 
                                        "asset": {"id": "G003", 
                                                  "name": "Sticks", 
                                                  "types": {"Tool", "Ground"}, 
                                                  "quantity": 6, 
                                                  "location_name": "SAR Base"}
                                        })
        agent.process_request({"message_type": "allocate", "asset_id": "G003", "team_id": "GroundTroop1", "quantity": 2})
        assert agent.kb.get_asset("G003").unallocated_quantity == 4

        print(agent.kb.get_all_assets())
        output = agent.process_request({"message_type": "return", "asset_id": "G003", "team_id": "GroundTroop1", "quantity": 1})
        assert output["success"] == True
        assert agent.kb.get_asset("G003").quantity == 6
        assert agent.kb.get_asset("G003").unallocated_quantity == 5

        output = agent.process_request({"message_type": "return", "asset_id": "G003", "team_id": "GroundTroop1", "quantity": 1})
        assert output["success"] == True
        assert agent.kb.get_asset("G003").quantity == 6
        assert agent.kb.get_asset("G003").unallocated_quantity == 6
        assert output["message"] == "Returned all G003 units"

        output = agent.process_request({"message_type": "return", "asset_id": "G003", "team_id": "GroundTroop1", "quantity": 1})
        assert output["success"] == True
        assert output["message"] == "Returned 1 extra units, updated asset quantity"
        assert agent.kb.get_asset("G003").quantity == 7
        assert agent.kb.get_asset("G003").unallocated_quantity == 7

