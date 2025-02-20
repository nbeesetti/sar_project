from sar_project.agents.base_agent import SARBaseAgent
from sar_project.knowledge.asset_knowledge_base import AssetKnowledgeBase

"""
** Asset Manager Agent for SAR Operations **
@author: Neeraja Beesetti
Takes requests as input, does some processing,
fetches/updates data from the knowledge base, 
returns a response in dict format { "key": "value" }
Responses contains a boolean "success" field to indicate if processing request went through
"""

class AssetManagerAgent(SARBaseAgent):
    def __init__(self, name="asset_manager"):
        super().__init__(
            name=name,
            role="Asset Manager",
            system_message="""You are a asset manager for SAR operations. Your role is to:
            1. Maintain a comprehensive inventory of all assets
            2. Allocate assets to teams and tasks
            3. Schedule asset maintenance
            4. Monitor location and status of all assets
            5. Track asset efficiency
            6. Manage asset lifecycle
            7. Make sure assets meet regulations and safety standards
            8. Generate reports on asset status, utilization, and performance""",
            knowledge_base = AssetKnowledgeBase()
        )

        self.populate_kb()   
        self.update_status("active") 

    def populate_kb(self):
        """Populate the knowledge base with some initial assets"""
        self.kb.add_asset(
            id="A001",
            name="Drone",
            types={"UAV", "Camera", "Aerial"},
            quantity=5,
            location_name="SAR Base",
        )
        self.kb.add_asset(
            id="A002",
            name="Helicopter",
            types={"Vehicle", "Aerial"},
            quantity=1,
            location_name="SAR Base",
        )
        self.kb.add_asset(
            id="W001",
            name="Rescue Boat",
            types={"Vehicle", "Boat", "Water"},
            quantity=2,
            location_name="SAR Dock",
        )
        self.kb.add_asset(
            id="M010",
            name="Medical Kit",
            types={"First Aid", "Medical"},
            quantity=10,
            location_name="SAR Base",
        )
        
    def update_status(self, status):
        """Update the agent's status"""
        self.status = status
        return {"status": "updated", "new_status": status}

    def get_status(self):
        """Get the agent's current status"""
        return getattr(self, "status", "unknown")
    
    def process_request(self, message):
        """Process asset-related requests"""
        m = message["message_type"]
        try:
            if "find_asset_id" in m:
                return self.find_asset_id(message.get("name"))
            elif "get_all_assets" in m:
                return self.get_all_assets()
            elif "add_asset" in m:
                return self.add_asset(message)
            elif "update_asset" in m:
                return self.update_asset(message)
            elif "remove_asset" in m:
                return self.remove_asset(message)
            elif "allocate" in m:
                return self.allocate_asset(message)
            elif "return" in m:
                return self.return_asset(message)
            else:
                return {"error": "Unknown request type"}
        except Exception as e:
            return {"error": str(e)}
    
    def find_asset_id(self, asset_name):
        asset = self.kb.get_asset_by_name(asset_name)
        if asset:
            return {"success": True, "asset_id": asset.id}
        else:
            return {"success": False, "error": "Asset not found"}

    def get_all_assets(self):
        assets = self.kb.get_all_assets()
        return {"all_assets": assets}
    
    def add_asset(self, message):
        asset_dict = message.get("asset")
        if "name" not in asset_dict or "types" not in asset_dict:
            return {"success": False, "error": "Asset name and types are required"}
        if self.kb.get_asset_by_name(asset_dict["name"]):
            return {"success": False, "error": "Asset already exists, use update_asset instead"}
        self.kb.add_asset(**asset_dict)
        return {"success": True, "asset_added": str(asset_dict)}
    
    def resolve_message_name_to_id(self, asset_id, asset_name):
        if not asset_id and not asset_name: return (False, "Asset ID or Name is required")
        if asset_name:
            asset_id = self.kb.get_asset_id_by_name(asset_name)
            if asset_id is None:
                return (False, "Asset not found")
        asset = self.kb.get_asset(asset_id)
        if not asset:
            return (False, "Asset ID not found")
        return (True, asset.id)

    def update_asset(self, message):
        ''' Currently only supports updating asset types, quantity, and location'''
        success, asset_id_or_msg = self.resolve_message_name_to_id(message.get("id"), message.get("name"))
        if not success: 
            return {"success": False, "error": asset_id_or_msg}
        asset_id = asset_id_or_msg

        field = message.get("update_field")
        if field == "types":
            if message.get("types") is None:
                return {"success": False, "error": "types field is required"}
            self.kb.update_asset_types(asset_id, message["types"], replace=message.get("replace", False))
        elif field == "quantity":
            if message.get("quantity") is None:
                return {"success": False, "error": "quantity field is required"}
            self.kb.update_asset_quantity(asset_id, message["quantity"], replace=message.get("replace", False))
        elif field == "location":
            if message.get("location") is None:
                return {"success": False, "error": "location field is required"}
            self.kb.update_asset_location(asset_id, message["location"])
        else:
            return {"success": False, "error": "Unsupported update_field"}
        
        return {"success": True, "asset_updated": str(self.kb.get_asset(asset_id))}

    def remove_asset(self, message):
        success, asset_id_or_msg = self.resolve_message_name_to_id(message.get("id"), message.get("name"))
        if not success: 
            return {"success": False, "error": asset_id_or_msg}
        asset_id = asset_id_or_msg

        self.kb.remove_asset(asset_id)
        return {"success": True, "asset_removed": asset_id}

    def allocate_asset(self, message):
        asset_id = message.get("asset_id")
        team_id = message.get("team_id")
        quantity = message.get("quantity")
        if not asset_id or not team_id or not quantity:
            return {"success": False, "error": "asset_id, team_id, and quantity are required"}
        success, msg = self.kb.allocate_asset(asset_id, team_id, quantity)
        if not success:
            return {"success": False, "error": msg}
        else:
            return {"success": True, "message": msg}
    
    def return_asset(self, message):
        asset_id = message.get("asset_id")
        team_id = message.get("team_id")
        quantity = message.get("quantity")
        if not asset_id or not team_id or not quantity:
            return {"success": False, "error": "asset_id, team_id, and quantity are required"}
        success, msg = self.kb.return_asset(asset_id, team_id, quantity)
        if not success:
            return {"success": success, "error": msg}
        else:
            return {"success": True, "message": msg}