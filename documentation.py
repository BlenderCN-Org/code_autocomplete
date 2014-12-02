import bpy, inspect
from collections import defaultdict

class Documentation:
    def __init__(self):
        pass
    
    def build(self):
        self.reset()
        all_bpy_types = inspect.getmembers(bpy.types)
        self.build_type_documentation(all_bpy_types)
        self.build_attribute_documentation(all_bpy_types)
        self.add_custom_properties() 
        self.categorize_attributes()
        
    def reset(self):
        self.types = defaultdict(TypeDocumentation)
        self.functions = []
        self.functions_by_name = defaultdict(list)
        self.functions_by_owner = defaultdict(list)
        self.properties = []
        self.properties_by_name = defaultdict(list)
        self.properties_by_owner = defaultdict(list)
        
    def build_type_documentation(self, bpy_types):
        for type in bpy_types:
            type_doc = self.get_documentation_of_type(type[1].bl_rna)
            self.types[type_doc.name] = type_doc
        
    def get_documentation_of_type(self, type):
        type_doc = TypeDocumentation(type.identifier)
        type_doc.description = type.description
        return type_doc
            
        
    def build_attribute_documentation(self, bpy_types):
        for type in bpy_types:
            self.build_attribute_lists_of_type(type[1])
              
    def build_attribute_lists_of_type(self, type):
        identifier = type.bl_rna.identifier
        
        for function in type.bl_rna.functions:
            function_doc = self.get_documentation_of_function(function, identifier)
            self.functions.append(function_doc)
            
        for property in type.bl_rna.properties:
            property_doc = self.get_documentation_of_property(property, identifier)
            self.properties.append(property_doc)
            
    def get_documentation_of_function(self, function, owner):
        function_doc = FunctionDocumentation(function.identifier)
        function_doc.description = function.description
        function_doc.owner = owner
        function_doc.inputs, function_doc.outputs = self.get_function_parameters(function)
        return function_doc
    
    def get_function_parameters(self, function):
        inputs = []
        outputs = []
        for parameter in function.parameters:
            parameter_doc = self.get_documentation_of_property(parameter, function.identifier)
            if parameter.is_output: outputs.append(parameter_doc)
            else: inputs.append(parameter_doc)
        return inputs, outputs
            
    def get_documentation_of_property(self, property, owner):
        property_doc = PropertyDocumentation(property.identifier)
        property_doc.type = self.get_property_type(property)
        if property_doc.type == "Enum":
            property_doc.enum_items = self.get_enum_items(property)
        property_doc.description = property.description
        property_doc.is_readonly = property.is_readonly
        property_doc.owner = owner
        return property_doc
    
    def get_property_type(self, property):
        type = property.type
        
        if type == "POINTER":
            return property.fixed_type.identifier
        
        if type == "COLLECTION":
            srna = getattr(property, "srna", None)
            if srna is None: return "bpy_prop_collection"
            else: return srna.identifier
        
        if type in ["FLOAT", "INT", "STRING", "BOOLEAN"]:
            array_length = getattr(property, "array_length", 0)
            type_name = self.convert_to_nicer_type(type)
            if array_length <= 1: return type_name
            elif array_length <= 3: return type_name + " Vector " + str(array_length)
            else: return type_name + " Array " + str(array_length)
        
        if type == "ENUM":
            return "Enum"
        
        return None
    
    def get_enum_items(self, enum_property):
        items = []
        for item in enum_property.enum_items:
            items.append(item.identifier)
        return items
    
    def convert_to_nicer_type(self, type):
        if type == "INT": return "Integer"
        if type == "FLOAT": return "Float"
        if type == "BOOLEAN": return "Boolean"
        if type == "STRING": return "String"

    
    # have to do this manually, because these properties aren't available everywhere
    def add_custom_properties(self):
        props = self.properties
        
        # Screen Context
        props.append(PropertyDocumentation("visible_objects", type = "Object Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("visible_bases", type = "ObjectBase Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("selectable_objects", type = "Object Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("selectable_bases", type = "ObjectBase Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("selected_objects", type = "Object Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("selected_bases", type = "ObjectBase Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("selected_editable_objects", type = "Object Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("selected_editable_bases", type = "ObjectBase Sequence", is_readonly = True, owner = "Context"))
        
        props.append(PropertyDocumentation("visible_bones", type = "EditBone Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("editable_bones", type = "EditBone Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("selected_bones", type = "EditBone Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("selected_editable_bones", type = "EditBone Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("visible_pose_bones", type = "PoseBone Sequence", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("selected_pose_bones", type = "PoseBone Sequence", is_readonly = True, owner = "Context"))
        
        props.append(PropertyDocumentation("active_bone", type = "EditBone", is_readonly = True, owner = "Context"))
        props.append(PropertyDocumentation("active_pose_bone", type = "PoseBone", is_readonly = True, owner = "Context"))
      
        props.append(PropertyDocumentation("active_base", type = "ObjectBase", owner = "Context"))
        props.append(PropertyDocumentation("active_object", type = "Object", owner = "Context"))
        props.append(PropertyDocumentation("object", type = "Object", owner = "Context"))
        props.append(PropertyDocumentation("edit_object", type = "Object", owner = "Context"))
        props.append(PropertyDocumentation("sculpt_object", type = "Object", owner = "Context"))
        props.append(PropertyDocumentation("vertex_paint_object", type = "Object", owner = "Context"))
        props.append(PropertyDocumentation("weight_paint_object", type = "Object", owner = "Context"))
        props.append(PropertyDocumentation("image_paint_object", type = "Object", owner = "Context"))
        props.append(PropertyDocumentation("particle_edit_object", type = "Object", owner = "Context"))
        
        props.append(PropertyDocumentation("sequences", type = "Sequence Sequence", owner = "Context"))
        props.append(PropertyDocumentation("selected_sequences", type = "Sequence Sequence", owner = "Context"))
        props.append(PropertyDocumentation("selected_editable_sequences", type = "Sequence Sequence", owner = "Context"))
        
        props.append(PropertyDocumentation("active_operator", type = "Operator", owner = "Context"))

    
    def categorize_attributes(self):
        for property in self.properties:
            self.properties_by_name[property.name].append(property)
            self.properties_by_owner[property.owner].append(property)
            
        for functions in self.functions:
            self.functions_by_name[functions.name].append(functions)
            self.functions_by_owner[functions.owner].append(functions)
            
            
    def get_subproperty_names_of_property(self, property_name):
        return list(set([property.name for property in self.get_subproperties_of_property(property_name)]))   
            
    def get_subproperties_of_property(self, property_name):
        properties = []
        for type in self.get_possible_property_types(property_name):
            properties.extend(self.get_properties_of_type(type))
        return properties
            
    def get_types_with_property(self, property_name):
        return [property.owner for property in self.properties_by_name[property_name]]
    
    def get_property_names_of_type(self, type_name):
        return [property.name for property in self.get_properties_of_type(type_name)]
    
    def get_properties_of_type(self, type_name):
        return self.properties_by_owner[type_name]
    
    def get_type_description(self, type_name):
        return self.types[type_name].description
    
    def get_possible_property_types(self, property_name):
        return list(set([property.type for property in self.get_possible_properties(property_name)]))
    
    def get_possible_property_descriptions(self, property_name):
        return list(set(property.description for property in self.get_possible_properties(property_name)))
    
    def get_possible_properties(self, property_name):
        return self.properties_by_name[property_name]
    
    def get_function_names_of_type(self, type_name):
        return [function.name for function in self.get_functions_of_type(type_name)]
    
    def get_functions_of_type(self, type_name):
        return self.functions_by_owner[type_name]
        
        
class PropertyDocumentation:
    def __init__(self, name = "", description = "", type = None, owner = None, is_readonly = False, enum_items = []):
        self.name = name
        self.description = description
        self.type = type
        self.owner = owner
        self.is_readonly = is_readonly
        self.enum_items = enum_items
        
    def __repr__(self):
        return self.owner + "." + self.name
        
        
class FunctionDocumentation:
    def __init__(self, name = "", description = "", owner = None, inputs = [], outputs = []):
        self.name = name
        self.description = description
        self.owner = owner
        self.inputs = inputs
        self.outputs = outputs
        
    def get_input_names(self):
        return [input.name for input in self.inputs]
    def get_output_names(self):
        return [output.name for output in self.outputs]
   
    def __repr__(self):
        output_names = ", ".join(self.get_output_names())
        if output_names != "": output_names = " -> " + output_names
        return self.name + "(" + ", ".join(self.get_input_names()) + ")" + output_names
        
        
class TypeDocumentation:
    def __init__(self, name = "", description = ""):
        self.name = name
        self.description = description 

    def __repr__(self):
        return self.name