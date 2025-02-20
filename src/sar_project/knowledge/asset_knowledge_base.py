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
        # self.status = AssetStatus.AVAILABLE
        self.location_GPS = location_GPS # (latitude, longitude) in Decimal Degrees coordinates
        self.location_name = location_name
        self.allocated = (False, None) # or (True, team_id)
        self.unallocated_quantity = self.quantity
    
    def __repr__(self):
        return f"Asset {self.name} ({self.id}) of {self.types} at {self.location_name} ({self.location_GPS}) with {self.quantity} total units, {self.unallocated_quantity} available, allocation status: {self.allocated}"
    
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
            # print("Asset not found")
            return None
    
    def get_asset_id_by_name(self, asset_name):
        if asset_name in self.ids_by_name:
            return self.ids_by_name[asset_name]
        else:
            # print("Asset not found")
            return None
    
    def get_asset(self, asset_id):
        if asset_id in self.assets_by_id:
            return self.assets_by_id[asset_id]
        else:
            # print("Asset not found")
            return None

    def add_asset(self, name, types: set, id=uuid.uuid4(), quantity=1, location_name="", location_GPS=(0,0)):
        ''' Required parameters: name, types'''
        asset = Asset(id=id, name=name, types=types, quantity=quantity, location_name=location_name, location_GPS=location_GPS)
        self.assets_by_id[asset.id] = asset
        self.ids_by_name[asset.name] = asset.id
        self.updateUsageLog(asset, action="create", datetime=datetime.now())
    
    def remove_asset(self, asset_id):
        asset = self.get_asset(asset_id)
        if asset:
            del self.ids_by_name[asset.name]
            del self.assets_by_id[asset.id]
    
    def update_asset_quantity(self, asset_id, quantity, replace=False):
        asset = self.get_asset(asset_id)
        if asset:
            if replace:
                asset.quantity = quantity
            else:
                asset.quantity += quantity
    
    def update_asset_types(self, asset_id, add_types, replace=False):
        asset = self.get_asset(asset_id)
        if asset:
            if replace:
                asset.types = add_types
            else:
                asset.types.update(add_types)

    def update_asset_location(self, asset_id, location):
        """
        Updates the location of an asset.

        Args:
            asset_id (str): Unique identifier of the asset.
            location: either a tuple (latitude, longitude) or a string "location_name".
        """
        asset = self.get_asset(asset_id)
        if asset:
            if isinstance(location, tuple):
                asset.location_GPS = location
            else:
                asset.location_name = location
    
    def updateUsageLog(self, asset_id, action, datetime, team_id=None, **kwargs):
        self.log.append(
            {
                "asset_id": asset_id,
                "action": action, 
                "datetime": datetime,
                "team_id": team_id,
                **kwargs
            }
        )
    
    def log_allocation(self, asset_id, team_id, **kwargs):
        if self.get_asset(asset_id):
            self.updateUsageLog(asset_id, UsageLogAction.ALLOCATED, datetime.now(), team_id, **kwargs)
    
    def allocate_asset(self, asset_id, team_id, quantity):
        asset = self.get_asset(asset_id)
        if asset:
            if asset.unallocated_quantity < quantity:
                return (False, f"Not enough units available, {asset.unallocated_quantity} units remaining")
            asset.unallocated_quantity -= quantity
            asset.allocated = (True, team_id)
            self.log_allocation(asset_id, team_id, quantity=quantity)
            return (True, f"Asset {asset_id} allocated to team {team_id}, {asset.unallocated_quantity} units remaining")
        return (False, "Asset not found")
    
    def log_return(self, asset_id, team_id, **kwargs):
        if self.get_asset(asset_id):
            self.updateUsageLog(asset_id, UsageLogAction.RETURNED, datetime.now(), team_id, **kwargs)
    
    def return_asset(self, asset_id, team_id, quantity):
        # TO DO: change allocations to be list of (team_id, quantity) tuples to track who owns how many
        # for now, assume only one team can allocate an asset, regardless of remaining quantity
        asset = self.get_asset(asset_id)
        if quantity <= 0: return (False, "Quantity must be greater than 0")
        if asset:
            asset.unallocated_quantity += quantity
            self.log_return(asset_id, team_id, quantity=quantity)
            if asset.unallocated_quantity > asset.quantity:
                # returned more than original quantity
                extra = asset.unallocated_quantity - asset.quantity
                asset.quantity = asset.unallocated_quantity
                asset.allocated = (False, None)
                return (True, f"Returned {extra} extra units, updated asset quantity")
            elif asset.unallocated_quantity < asset.quantity:
                # some returned, some assets still allocated
                still_allocated = asset.quantity - asset.unallocated_quantity
                return (True, f"Returned {quantity} units, {still_allocated} units still in use")
            else:
                # returned all
                asset.allocated = (False, None)
                return (True, f"Returned all {asset_id} units")
        return (False, "Asset not found")

    def get_asset_usage_log(self, asset_id):
        if self.get_asset(asset_id):
            return [log for log in self.log if log["asset_id"] == asset_id]
        
    def get_all_assets(self):
        return self.assets_by_id.items()
    
    def get_assets_by_type(self, asset_type):
        return [asset for asset in self.assets_by_id.values() if asset_type in asset.types]
    
    def get_assets_by_status(self, status):
        return [asset for asset in self.assets_by_id.values() if asset.status == status]
    
