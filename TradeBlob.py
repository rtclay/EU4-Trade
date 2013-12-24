class world_data:
    def __init__(self):
        self.countries = []
        self.trade_nodes = ()

class trade_ship:
    id_number = 0
    def __init__(self):
        self.trade_power= 0
        self.id_number = id_number
        id_number = id_number + 1

class trade_fleet:
    def __init__(self):
        #self.trade_ships = []
        self.raw_power=0
        self.leader = None
        
    def get_leader_maneuver(self):
        return self.leader.maneuver
        
    def cooked_power(self):
        return self.raw_power*(1+.05*self.get_leader_maneuver)
        
    def set_trade_power(self, power):
        self.raw_power= power
        
class leader:
    def __init__(self):
        self.maneuver = 0
        
class merchant:
    id_number = 0
    def __init__(self, country):
        self.mission = None
        self.node = None
        self.country = country
        self.target_node = None
        self.id_number = id_number
        id_number = id_number + 1
        
    def is_collecting(self):
        return mission == "collecting"
      
    def is_steering(self):
        return mission == "steering"
    
    def is_working_in(self, node):
        return self.node == node and self.mission !=None
      
    def get_steering_target(self):
        return self.target_node
        
    def get_country(self):
        return self.country
        
    def assign_merchant(self, node, mission, target_node=None):
        self.node = node
        self.mission = mission
        self.target_node = target_node
        
          
    def recall_merchant(self):
        self.node=None
        self.mission = None
        self.target_node = None
        
    def __repr(self):
        return "Merchant "+str(self.id_number)

class country:
    id_number = 0
    
    def __init__(self, name=None, capital_node, merchant_number):
        if name != None:
            self.name = name
        else:
            self.name= ""
        self.capital_node = capital_node
        #TODO need to change these modifiers to match the modifiers in the game ie default at 0 or 1
        self.trade_steering = 1.0
        self.trade_income_modifier = 1.0
        self.trade_efficiency = 0.0
        self.mercantilism = 0.0
        self.trade_range = None
        self.embargo_targets = []
        self.trade_ships = []
        self.current_scheme = None
        self.merchant_number = merchant_number
        
    def get_capital(self):
        return self.capital_node
      
    def __repr__(self):
        return "Country " +self.name
      
    def __eq__(self, other):
        try:
            return self.name == other.name 
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
  

class trade_node:
    id_number = 0
    
    def __init__(self, name=None, in_nodes=(),out_nodes=()):
        if name != None:
            self.name = name
        else:
            self.name= ""
        self.in_nodes = in_nodes
        self.out_nodes = out_nodes
        self.active_countries = []
        self.value_local = 0
        self.id_number = id_number
        id_number = id_number + 1
        
    def __repr__(self):
        return "Trade Node " +self.name
      
    def __eq__(self, other):
        try:
            return self.name == other.name and self.in_nodes == other.in_nodes and self.out_nodes == other.out_nodes
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
        
    
      
class trade_state:
    def __init__(self, data):
        self.nodes = data.trade_nodes
        self.countries = data.countries
        self.node_province_power = dict()#a dictionary pairing nodes to (dictionaries pairing countries to power)
        self.node_fleet_power = dict()#a dictionary pairing nodes to (dictionaries pairing countries to power) 
        self.node_local_value = dict()
        self.node_incoming_value = dict()#a dictionary pairing nodes to incoming trade values, memoized to avoid lots of recursion 
        self.merchants = []
        for cty in self.countries:
            for merch in cty.merchant_number:
                self.merchants.append(merchant(cty))
        
     def get_power_modifier_in_node(self, country, node):
        if node == country.capital_node:
            return 1.0 + country.trade_efficiency
        else:
            if self.is_country_collecting(country, node):
                return (1.0 + country.trade_efficiency) * 0.5
        return 1.0 + country.trade_efficiency
        
    def is_country_collecting(self, country, node):
        if country.get_capital() == node:
            return True
        if [(merch.is_collecting() and merch.is_working_in(node)) for merch in country.merchants]:
            return True
        else:
            return False
    
    def is_country_forwarding(self, country, node):
        if [(merch.is_steering() and merch.is_working_in(node)) for merch in country.merchants]:
            return True
        if get_country_power_in_node(country, node) >0 and not self.is_country_collecting(country, node):
            return True
        else:
            return False
          
    def is_country_steering(self, country, node):
        if [(merch.is_steering() and merch.is_working_in(node)) for merch in country.merchants]:
            return True
        else:
            return False
    
    def has_merchant_in_node(self, country, node):
        return len([ merch.is_working_in(node) for merch in country.merchants]) > 0
        
    def get_country_power_in_node(self, country, node):
        return self.get_power_modifier_in_node(country, node) * (self.node_province_power[node][country] + self.node_fleet_power[node][country] + int(self.has_merchant_in_node(country,node))*2)
      
    def get_collecting_power(self, node):
        return sum([self.get_country_power_in_node(ctry,node) for ctry in self.countries if self.is_country_collecting(ctry, node)])
      
    def get_forwarding_power(self, node):
        return sum([self.get_country_power_in_node(ctry,node) for ctry in self.countries if self.is_country_forwarding(ctry, node)])
      
    def get_total_power(self, node):
        return sum([self.get_country_power_in_node(ctry,node) for ctry in self.countries])
      
      
    def get_steering_powers(self, fromNode):
        merchants_steering_in_node = [merch for merch in self.merchants if (merch.is_steering() and merch.is_working_in(fromNode))]
        outnodes= fromNode.out_nodes
        outnode_powers = dict.fromkeys(outnodes, 0)
       
        #list of countries that are forwarding in the trade node
        #[country for country in self.countries if (self.get_country_power_in_node(country, fromNode) >0 and self.is_country_forwarding(country, fromNode))]:
        for merch in merchants_steering_in_node:           
            country = merch.get_country()            
            outnode_powers[merch.get_steering_target()]= outnode_powers[merch.get_steering_target()] + (self.get_country_power_in_node(country, fromNode) * country.trade_steering)
            
            
        return outnode_powers.viewitems()
      
    def get_total_steering_power(self, node)
        return sum([power for (nde, power) in self.get_steering_powers(node)])
        
    def get_local_value(self, node):
        return self.node_local_value.get(node, 0)
                                         
    def get_incoming_value(self, node):
        if node in self.node_incoming_value:
            return self.node_incoming_value.get(node)
        else:
            self.node_incoming_value[node] = sum([self.get_outgoing_value(from_node, node) for from_node in node.in_nodes])
            return self.node_incoming_value.get(node)
          
    def get_value(self, node):
        return self.get_local_value(node) + self.get_incoming_value(node)
    
    def get_outgoing_value(self, from_node, to_node):
        power_favorable = [power for (nde, power) in self.get_steering_powers(from_node) if nde == to_node][0]        
        return self.get_value(from_node) * self.get_forwarding_power(from_node) / self.get_total_power(from_node) * power_favorable / self.get_total_steering_power(from_node) * (1+ self.get_merchant_boost(node))
        
    def get_merchant_boost(self, node):
        #NOTE does not calculate the increase to the bonus deriving from trade steering
        bonuses = [0.0, .05, .075, .091, .103, .113]
        try:
            return bonus[len([1 for merch in self.merchants if merch.is_working_in(node)])]
        catch:
            return .113
          
    def get_collected_value(self, country, node):
        if self.has_merchant_in_node(country, node) and  country.get_capital() == node:
            return 1.1* self.get_value(node) * country.trade_income_modifier / self.get_total_power(node) * self.get_country_power_in_node(country, node)
        elif self.has_merchant_in_node(country, node) or country.get_capital() == node:
            return self.get_value(node) * country.trade_income_modifier / self.get_total_power(node) * self.get_country_power_in_node(country, node)   
        else:
            return 0
          
            
    def get_revenue(self, country):
        return sum([self.get_collected_value(country, node) for node in self.nodes])
    
    def get_power_share(self, country, node):
        return self.get_country_power_in_node(country, node) / self.get_total_power(node)
   
    def get_marginal_value(self, country, node):
        #TODO make this calculate effect of merchant and capital when collecting
        favorable_node = [merchant.get_steering_target() for merchant in country.merchants if merchant.is_working_in(node)][0]
        favorable_power = [power for (nde, power) in self.get_steering_powers(from_node) if nde == to_node][0] 
        
        if self.is_country_collecting(country, node):
            return (1+country.trade_income_modifier) * self.get_value(node) * (1 - self.get_power_share(country, node)) / self.get_total_power(node)
        if self.is_country_steering(country, node):
            return (1+self.get_merchant_boost(node)) * self.get_value(node) * (1 - self.get_forwarding_power(node)) / self.get_total_power(node) + (1+self.get_merchant_boost(node)) * self.get_outgoing_value(node, favorable_node)*(1 - favorable_power/self.get_total_steering_power(node)) / self.get_total_steering_power(node)      
        if self.is_country_forwarding(country, node) #when it gets to this point the country is not steering, only forwarding
            return (1+self.get_merchant_boost(node)) * self.get_value(node) * (1 - self.get_forwarding_power(node)) / self.get_total_power(node)
      
 
      

      
sevilla = trade_node("Sevilla",(caribbean, mauritania, genoa, safi, tunis), (bordeaux))
bordeaux = trade_node("Bordeaux",(caribbean, chesapeake, sevilla),(london))
london = trade_node("London",(north_sea, bordeaux),(antwerpen))
antwerpen = trade_node("Antwerpen",(lubeck, london, genoa, frankfurt, bordeaux),())
north_sea = trade_node("North Sea",(hudson, chesapeake, white_sea),(lubeck, london))
chesapeake = trade_node("Chesapeake",(caribbean, mississippi),(bordeaux, london, north_sea))
mississippi = trade_node("Mississippi",(),(chesapeake, caribbean))
caribbean = trade_node("Caribbean",(mexico, panama),(sevilla, chesapeake))
mexico = trade_node("Mexico",(california),(caribbean, panama, nippon))
panama = trade_node("Panama", (mexico, philippines, peru),(caribbean))
brazil = trade_node("Brazil", (), (ivory_coast))
peru = trade_node("Peru",(),(panama))
california = trade_node("California", (), (mexico))
canton = trade_node("Canton", (), (malacca, hangzhou))
venice = trade_node("Venice", (ragusa, alexandria, wien), ())
genoa = trade_node("Genoa", (tunis, alexandria), (sevilla))
tunis = trade_node("Tunis",(timbuktu),(sevilla, genoa))
mauritania = trade_node("Mauritania", (timbuktu, ivory_coast), (sevilla))
lubeck = trade_node("Lubeck",(wien, frankfurt, baltic, north_sea),(antwerpen)
baltic = trade_node("Baltic Sea", (), (lubeck))
constantinople = trade_node("Constantinople",(alexandria, crimea, basra),(ragusa))
basra = trade_node("Basra",(indus),(constantinople))
ragusa = trade_node("Ragusa", (constantinople), (venice))
alexandria = trade_node("Alexandria", (aden),(genoa, constantinople, venice))
crimea = trade_node("Crimea",(astrakhan), (constantinople, kiev))
zanzibar = trade_node("Zanzibar", (aden), (cape))
aden = trade_node("Gulf of Aden", (indus, ceylon), (zanzibar, alexandria, basra))
cape = trade_node("Cape of Good Hope", (zanzibar), (congo))
congo = trade_node("Congo", (ivory_coast), (cape))
ivory_coast = trade_node("Ivory Coast", (congo), (mauritania, timbuktu))
timbuktu = trade_node("Timbuktu", (ivory_coast), (mauritania, tunis))
indus = trade_node("Indus River", (ceylon, kashmir), (aden))
ceylon = trade_node("Ceylon", (bengal), (indus, aden))
bengal = trade_node("Bengal", (malacca), (ceylon))
malacca = trade_node("Malacca", (philippines), (bengal))
philippines = trade_node("Philippines", (australia), (malacca, panama))
australia = trade_node("Australia", (), (phillipines))
nippon = trade_node("Nippon", (mexico), (hangzhou))
hudson = trade_node("Hudson Bay", (), (north_sea))
samarkand = trade_node("Samarkand", (yumen, kashmir), (astrakhan, persia))
astrakhan = trade_node("Astrakhan", (samarkand), (kazan,crimea))
kiev = trade_node("Kiev", (crimea), (venice))
siam = trade_node("Siam", (), (malacca))
yumen = trade_node("Yumen", (beijing, hangzhou), (samarkand))
kashmir = trade_node("Kashmir", (), (samarkand, indus))
hangzhou = trade_node("Hangzhou", (beijing, canton, nippon), (yumen, malacca))
persia = trade_node("Persia", (samarkand), (constantinople))
kazan = trade_node("Kazan", (crimea), (venice))
novgorod = trade_node("Novgorod", (kiev, kazan), (white_sea, north_sea))
safi = trade_node("Safi", (timbuktu), (sevilla))
krakow = trade_node("Krakow", (kiev), (wien, baltic))
wien = trade_node("Wien", (ragusa, krakow), (venice, frankfurt, lubeck))
frankfurt = trade_node("Frankfurt", (wien), (antwerpen, lubeck))
white_sea = trade_node("White Sea", (novgorod), (north_sea))
beijing = trade_node("Beijing", (), (yumen, hangzhou))



nodes = (sevilla, bordeaux, london, antwerpen, north_sea, chesapeake, mississippi, caribbean, mexico, panama, brazil, peru, california, venice, genoa, tunis, mauritatnia, lubeck, baltic, constantinople, baghdad, riga, alexandria, crimea, zanzibar, aden, cape, congo, ivory_coast, timbuktu, indus, ceylon, bengal, malacca, phillipines, australia, nipon, hudson, samarkand, astrakhan, kiev, siam, yumen, kashmir, hangzhou, persia, kazan, novgoroad, safi, krakow, wien, frankfurt, white_sea, beijing)


portugal = country("Portugal", sevilla)
spain = country("Spain", sevilla)
england = country("England", london)
countries = [spain, portugal, england]


simple_world = world_data(countries, nodes)
