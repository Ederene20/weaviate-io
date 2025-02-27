# Howto: Manage-data/Cross-references - Python examples

# ================================
# ===== INSTANTIATION-COMMON =====
# ================================

import weaviate
from weaviate import WeaviateClient
from weaviate.classes.query import QueryReference
import weaviate_datasets
from typing import List
import os

# Instantiate the client anonymously
client = weaviate.connect_to_local(
    headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_APIKEY")}
)

# https://stackoverflow.com/questions/76171703/in-weaviate-how-to-remove-a-property-in-existing-class/76177363#76177363
# class_name is required to avoid the warning to use "class namespaced APIs"
# def del_prop(uuid: str, prop_name: str, class_name: str) -> None:
#     global client
#     object_data = client.data_object.get(uuid, class_name=class_name)
#     if prop_name in object_data["properties"]:
#         del object_data["properties"][prop_name]
#     client.data_object.replace(object_data["properties"], class_name, uuid)

def del_props(client: WeaviateClient, uuid_to_update: str, collection_name: str, prop_names: List[str]) -> None:
    collection = client.collections.get(collection_name)

    # fetch the object to update
    object_data = collection.query.fetch_object_by_id(uuid_to_update, include_vector=True)
    properties_to_update = object_data.properties

    # remove unwanted properties
    for prop_name in prop_names:
        if prop_name in properties_to_update:
            del properties_to_update[prop_name]

    # replace the properties
    collection.data.replace(
        uuid=uuid_to_update,
        properties=properties_to_update,
        vector=object_data.vector["default"]
    )


# ===========================================================
# ===== Define classes in the schema and upload dataset =====
# ===========================================================

client.collections.delete(["JeopardyQuestion", "JeopardyCategory"])

from weaviate.classes.config import Property, DataType

client.collections.create(
    name="JeopardyCategory",
    description="A Jeopardy! category",
    properties=[
        Property(name="title", data_type=DataType.TEXT)
    ]
)

# START CrossRefDefinition
from weaviate.classes.config import Property, DataType, ReferenceProperty

client.collections.create(
    name="JeopardyQuestion",
    description="A Jeopardy! question",
    properties=[
        Property(name="question", data_type=DataType.TEXT),
        Property(name="answer", data_type=DataType.TEXT),
    ],
    # highlight-start
    references=[
        ReferenceProperty(
            name="hasCategory",
            target_collection="JeopardyCategory"
        )
    ]
    # highlight-end

)
# END CrossRefDefinition

dataset = weaviate_datasets.JeopardyQuestions1k()  # instantiate dataset
dataset.upload_objects(client)  # batch-upload objects

questions = client.collections.get("JeopardyQuestion")
categories = client.collections.get("JeopardyCategory")

question_obj_id = questions.query.fetch_objects(limit=1).objects[0].uuid
category_obj_id = categories.query.fetch_objects(limit=1).objects[0].uuid
category_obj_id_alt = categories.query.fetch_objects(limit=2).objects[1].uuid


# ==========================================
# ===== Add an object with a cross-ref =====
# ==========================================

# Prep data
from weaviate.util import generate_uuid5

categories = client.collections.get("JeopardyCategory")
category_properties = {"title": "Weaviate"}
category_uuid = generate_uuid5(category_properties)
categories.data.insert(
    properties=category_properties,
    uuid=category_uuid
)
properties = {
    "question": "What tooling helps make Weaviate scalable?",
    "answer": "Sharding, multi-tenancy, and replication"
}

obj_uuid = generate_uuid5(properties)

# START ObjectWithCrossRef
questions = client.collections.get("JeopardyQuestion")

questions.data.insert(
    properties=properties,  # A dictionary with the properties of the object
    uuid=obj_uuid,  # The UUID of the object
    # highlight-start
    references={"hasCategory": category_uuid},  # e.g. {"hasCategory": "583876f3-e293-5b5b-9839-03f455f14575"}
    # highlight-end
)

# END ObjectWithCrossRef

# Test results
result = questions.query.fetch_object_by_id(
    obj_uuid,
    return_references=QueryReference(
        link_on="hasCategory"
    )
)
assert result.collection == "JeopardyQuestion"
xref_ids = [o.uuid for o in result.references["hasCategory"].objects]
assert category_uuid == str(xref_ids[0])
# END Test results


# =================================
# ===== Add one-way cross-ref =====
# =================================

# START OneWay
questions = client.collections.get("JeopardyQuestion")

questions.data.reference_add(
    from_uuid=question_obj_id,
    from_property="hasCategory",
    # highlight-start
    to=category_obj_id
    # highlight-end
)
# END OneWay

# Test results
result = questions.query.fetch_object_by_id(
    question_obj_id,
    return_references=QueryReference(
        link_on="hasCategory"
    )
)
assert result.collection == "JeopardyQuestion"
xref_ids = [o.uuid for o in result.references["hasCategory"].objects]
assert category_obj_id in xref_ids
# END Test results


# # =======================================
# # ===== Add bidirectional cross-ref =====
# # =======================================

client.collections.delete(["JeopardyQuestion", "JeopardyCategory"])

# START Collections TwoWay Category1
from weaviate.classes.config import Property, DataType, ReferenceProperty

category = client.collections.create(
    name="JeopardyCategory",
    description="A Jeopardy! category",
    properties=[
        Property(name="title", data_type=DataType.TEXT)
    ]
)
# END Collections TwoWay Category1

# START Collections TwoWay Question
client.collections.create(
    name="JeopardyQuestion",
    description="A Jeopardy! question",
    properties=[
        Property(name="question", data_type=DataType.TEXT),
        Property(name="answer", data_type=DataType.TEXT),
    ],
    # highlight-start
    references=[
        ReferenceProperty(
            name="hasCategory",
            target_collection="JeopardyCategory"
        )
    ]
    # highlight-end
)
# END Collections TwoWay Question

dataset = weaviate_datasets.JeopardyQuestions1k()  # instantiate dataset
dataset.upload_objects(client)  # batch-upload objects


# START Collections TwoWay Category2
from weaviate.classes.config import ReferenceProperty

# Add the reference to JeopardyQuestion, after it was created
category = client.collections.get("JeopardyCategory")
# category.config.add_reference(
category.config.add_reference(
    # highlight-start
    ReferenceProperty(
        name="hasQuestion",
        target_collection="JeopardyQuestion"
    )
    # highlight-end
)
# END Collections TwoWay Category2

# Delete any existing cross-references from the source and target objects
del_props(client=client, uuid_to_update=question_obj_id, collection_name="JeopardyQuestion", prop_names=["hasCategory"])
# del_props(client=client, uuid_to_update=category_obj_id, collection_name="JeopardyCategory", prop_names=["hasQuestion"])

# TwoWay Python
# For the "San Francisco" JeopardyQuestion object, add a cross-reference to the "U.S. CITIES" JeopardyCategory object
questions = client.collections.get("JeopardyQuestion")
# highlight-start
questions.data.reference_add(
    from_uuid=question_obj_id,
    from_property="hasCategory",
    to=category_obj_id
)
# highlight-end

# For the "U.S. CITIES" JeopardyCategory object, add a cross-reference to "San Francisco"
categories = client.collections.get("JeopardyCategory")
# highlight-start
categories.data.reference_add(
    from_uuid=category_obj_id,
    from_property="hasQuestion",
    to=question_obj_id
)
# highlight-end
# END TwoWay Python

# Test results
result = categories.query.fetch_object_by_id(
    category_obj_id,
    return_references=QueryReference(
        link_on="hasQuestion"
    )
)
assert result.collection == "JeopardyCategory"
xref_ids = [o.uuid for o in result.references["hasQuestion"].objects]
assert question_obj_id in xref_ids
# END Test results


# ===================================
# ===== Add multiple cross-refs =====
# ===================================

# Delete any existing cross-references from the source object
del_props(client=client, uuid_to_update=question_obj_id, collection_name="JeopardyQuestion", prop_names=["hasCategory"])

# Multiple Python
from weaviate.classes.data import DataReference

questions = client.collections.get("JeopardyQuestion")

# highlight-start
refs_list = []
for temp_uuid in [category_obj_id, category_obj_id_alt]:
    ref_obj = DataReference(
        from_uuid=question_obj_id,
        from_property="hasCategory",
        to_uuid=temp_uuid
    )
    refs_list.append(ref_obj)

questions.data.reference_add_many(refs_list)
# highlight-end
# END Multiple Python

# Test results
result = questions.query.fetch_object_by_id(
    question_obj_id,
    return_references=QueryReference(
        link_on="hasCategory"
    )
)
assert result.collection == "JeopardyQuestion"
xref_ids = [o.uuid for o in result.references["hasCategory"].objects]
for temp_uuid in [category_obj_id, category_obj_id_alt]:
    assert temp_uuid in xref_ids
# END Test results


# ============================
# ===== Read cross-ref =====
# ============================

question_obj_id = questions.query.fetch_objects(limit=1).objects[0].uuid

# ReadCrossRef
from weaviate.classes.query import QueryReference

questions = client.collections.get("JeopardyQuestion")

# Include the cross-references in a query response
# highlight-start
response = questions.query.fetch_objects(  # Or `hybrid`, `near_text`, etc.
    limit=2,
    return_references=QueryReference(
        link_on="hasCategory",
        return_properties=["title"]
    )
)
# highlight-end

# Or include cross-references in a single-object retrieval
# highlight-start
obj = questions.query.fetch_object_by_id(
    uuid=question_obj_id,
    return_references=QueryReference(
        link_on="hasCategory",
        return_properties=["title"]
    )
)
# highlight-end

# END ReadCrossRef

# Test results
assert "title" in response.objects[0].references["hasCategory"].objects[0].properties.keys()
assert "title" in obj.references["hasCategory"].objects[0].properties.keys()
# END Test results


# ============================
# ===== Delete cross-ref =====
# ============================

# Delete Python
# From the "San Francisco" JeopardyQuestion object, delete the "MUSEUMS" category cross-reference
questions = client.collections.get("JeopardyQuestion")
# highlight-start
questions.data.reference_delete(
# highlight-end
    from_uuid=question_obj_id,
    from_property="hasCategory",
    to=category_obj_id
)
# END Delete Python

# Test results
result = questions.query.fetch_object_by_id(
    question_obj_id,
    return_references=QueryReference(
        link_on="hasCategory"
    )
)
assert result.collection == "JeopardyQuestion"
xref_ids = [o.uuid for o in result.references["hasCategory"].objects]
assert category_obj_id not in xref_ids
# END Test results


# # ============================
# # ===== Update cross-ref =====
# # ============================

# Update Python
# In the "San Francisco" JeopardyQuestion object, set the "hasCategory" cross-reference only to "MUSEUMS"
questions = client.collections.get("JeopardyQuestion")
# highlight-start
questions.data.reference_replace(
# highlight-end
    from_uuid=question_obj_id,
    from_property="hasCategory",
    to=category_obj_id
)
# END Update Python

# Test results
result = questions.query.fetch_object_by_id(
    question_obj_id,
    return_references=QueryReference(
        link_on="hasCategory"
    )
)
assert result.collection == "JeopardyQuestion"
xref_ids = [o.uuid for o in result.references["hasCategory"].objects]
assert category_obj_id in xref_ids
# END Test results

client.close()
