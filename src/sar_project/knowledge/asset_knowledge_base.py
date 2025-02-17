import uuid
from datetime import datetime

class AssetStatus:
    IN_USE = "in_use"
    AVAILABLE = "available"
    IN_MAINTENANCE = "in_maintenance"

class AssetType:
    FIELD_RESOURCE = "field"
    VEHICLE = "vehicle"
    INTERNAL_RESOURCE = "internal"

class UsageLogAction:
    CREATED = "create"
    ALLOCATED = "alloc"
    RETURNED = "return"

class Asset:
    def __init__(self, id=uuid.uuid4(), name="", types=set(), quantity=1, location_name="", location_GPS=(0,0)):
        self.id = id
        self.name = name
        self.types = types
        self.quantity = quantity
        self.status = AssetStatus.AVAILABLE
        self.location_GPS = location_GPS # (latitude, longitude)
        self.location_name = location_name
    
    def updateTypes(self, types, replace=False):
        if replace:
            self.types = types
        else:
            self.types.update(types)
    
    def updateStatus(self, status):
        self.status = status


class AssetKnowledgeBase:
    def __init__(self):
        self.assets_by_id = {} # {asset_id: Asset}
        self.ids_by_name = {} # {asset_name: asset_id}
        self.log = []
    
    def get_asset_by_name(self, asset_name):
        if asset_name in self.ids_by_name:
            return self.assets_by_id[self.ids_by_name[asset_name]]
        else:
            print("Asset not found")
            return None
    
    def get_asset(self, asset_id):
        if asset_id in self.assets_by_id:
            return self.assets[asset_id]
        else:
            print("Asset not found")
            return None

    def add_asset(self, id, name, types, quantity=1, location_name="", location_GPS=None):
        asset = Asset(id=id, name=name, types=types, quantity=quantity, location_name=location_name, location_GPS=location_GPS)
        self.assets_by_id[asset.id] = asset
        self.ids_by_name[asset.name] = asset.id
        self.updateUsageHistory(asset, action="create", time=datetime.now())
    
    def remove_asset(self, asset_id):
        asset = self.get_asset(asset_id)
        if asset:
            del self.ids_by_name[asset.name]
            del self.assets_by_id[asset.id]
    
    def update_asset_quantity(self, asset_id, additional_quantity=None, replace_quantity=None):
        asset = self.check_asset(asset_id)
        if asset:
            if additional_quantity is not None:
                asset.quantity += additional_quantity
            elif replace_quantity is not None:
                asset.quantity = replace_quantity

    def update_asset_location(self, asset_id, location):
        """
        Updates the location of an asset.

        Args:
            asset_id (str): Unique identifier of the asset.
            location: either a tuple (latitude, longitude) or a string "location_name".
        """
        asset = self.check_asset(asset_id)
        if asset:
            if isinstance(location, tuple):
                asset.location_GPS = location
            else:
                asset.location_name = location
    
    def updateUsageHistory(self, asset_id, action, datetime, team=None, **kwargs):
        self.log.append(
            {
                "asset_id": asset_id,
                "action": action, 
                "datetime": datetime,
                "team": team,
                **kwargs
            }
        )
    
    def log_allocation(self, asset_id, team, **kwargs):
        if self.get_asset(asset_id):
            self.updateUsageHistory(asset_id, UsageLogAction.ALLOCATED, datetime.now(), team, **kwargs)

    def log_return(self, asset_id, team, **kwargs):
        if self.get_asset(asset_id):
            self.updateUsageHistory(asset_id, UsageLogAction.RETURNED, datetime.now(), team, **kwargs)

    def get_asset_history(self, asset_id):
        if self.get_asset(asset_id):
            return [log for log in self.log if log["asset_id"] == asset_id]

    def get_asset(self, asset_id):
        if self.get_asset(asset_id):
            return self.assets_by_id[asset_id]
    
    def get_all_assets(self):
        return self.assets_by_id.values()
    
    def get_assets_by_type(self, asset_type):
        return [asset for asset in self.assets_by_id.values() if asset_type in asset.types]
    
    def get_assets_by_status(self, status):
        return [asset for asset in self.assets_by_id.values() if asset.status == status]
    
