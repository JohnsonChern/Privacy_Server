import json

fhir_template = json.loads(
    '''
    {
    "Attachment":{
      "contentType" : "code",
      "language" : "code",
      "data" : "base64Binary",
      "url" : "uri",
      "size" : "unsignedInt",
      "hash" : "base64Binary",
      "title" : "string",
      "creation" : "dateTime"
    },

    "Coding" :{
      "system" : "uri",
      "version" : "string",
      "code" : "code",
      "display" : "string",
      "userSelected" : "boolean"
    },
    "CodeableConcept":{
      "coding" : [ "Coding" ],
      "text" : "string"
    },

    "Quantity":{
      "value" : "decimal",
      "comparator" : "code",
      "unit" : "string",
      "system" : "uri",
      "code" : "code"
    },

    "Range":{
      "low" : "Quantity",
      "high" : "Quantity"
    },

    "Ratio":{
        "numerator" : "Quantity",
        "denominator" : "Quantity"
    },

    "Period":{
        "start":"dateTime",
        "end":"dateTime"
    },

    "SampledData":{
      "origin" : "Quantity",
      "period" : "decimal",
      "factor" : "decimal",
      "lowerLimit" : "decimal",
      "upperLimit" : "decimal",
      "dimensions" : "positiveInt",
      "data" : "string"
    },

    "Identifier":{
      "use" : "code",
      "type" : "CodeableConcept",
      "system" : "uri",
      "value" : "string",
      "period" : "Period",
      "assigner" : "Reference"
    },

    "HumanName":{
      "resourceType" : "string",

      "use" : "code",
      "text" : "string",
      "family" : ["string"],
      "given" : ["string"],
      "prefix" : ["string"],
      "suffix" : ["string"],
      "period" : "Period"
    },

    "Address":{
      "resourceType" : "string",

      "use" : "code",
      "type" : "code",
      "text" : "string",
      "line" : ["string"],
      "city" : "string",
      "district" : "string",
      "state" : "string",
      "postalCode" : "string",
      "country" : "string",
      "period" : "Period"
    },

    "ContactPoint":{
      "resourceType" : "string",

      "system" : "code",
      "value" : "string",
      "use" : "code",
      "rank" : "positiveInt",
      "period" : "Period"
    },

    "Timing":{
      "resourceType" : "string",

      "event" : ["dateTime"],
      "repeat" : {
        "boundsQuantity" : "Quantity",
        "boundsRange" : "Range",
        "boundsPeriod" : "Period",
        "count" : "integer",
        "duration" : "decimal",
        "durationMax" : "decimal",
        "durationUnits" : "code",
        "frequency" : "integer",
        "frequencyMax" : "integer",
        "period" : "decimal",
        "periodMax" : "decimal",
        "periodUnits" : "code",
        "when" : "code"
      },
      "code" : "CodeableConcept"
    },


    "signature":{
      "type" : ["Coding"],
      "when" : "instant",
      "whoUri" : "uri",
      "whoReference" :  "Reference",
      "contentType" : "code",
      "blob" : "base64Binary"
    },

    "Annotation":{
      "authorReference" : "Reference",
      "authorString" : "string",
      "time" : "dateTime",
      "text" : "string"
    },

    "Reference" :{

      "reference" : "string",
      "display" : "string"
    },

    "Patient" :{
      "resourceType" : "string",
      "identifier" : ["Identifier"],
      "active" : "boolean",
      "name" : ["HumanName"],
      "telecom" : ["ContactPoint"],
      "gender" : "code",
      "birthDate" : "date",
      "deceasedBoolean" : "boolean",
      "deceasedDateTime" : "dateTime",
      "address" : ["Address"],
      "maritalStatus" : "CodeableConcept",
      "multipleBirthBoolean" : "boolean",
      "multipleBirthInteger" : "integer",
      "photo" : ["Attachment"],
      "contact" : [{
        "relationship" : ["CodeableConcept"],
        "name" : "HumanName",
        "telecom" : ["ContactPoint"],
        "address" : "Address",
        "gender" : "code",
        "organization" : "Reference",
        "period" : "Period"
      }],
      "animal" : {
        "species" : "CodeableConcept",
        "breed" : "CodeableConcept",
        "genderStatus" : "CodeableConcept"
      },
      "communication" : [{
        "language" : "CodeableConcept",
        "preferred" : "boolean"
      }],
      "careProvider" : ["Reference"],
      "managingOrganization" : "Reference",
      "link" : [{
        "other" : "Reference",
        "type" : "code"
      }]
    },

    "Observation":{
      "resourceType" : "string",

      "identifier" : ["Identifier"],
      "status" : "code",
      "category" : "CodeableConcept",
      "code" : "CodeableConcept",
      "subject" : "Reference",
      "encounter" : "Reference",

      "effectiveDateTime" : "dateTime",
      "effectivePeriod" : "Period",
      "issued" : "instant",
      "performer" : ["Reference"],

      "valueQuantity" : "Quantity",
      "valueCodeableConcept" : "CodeableConcept",
      "valueString" : "string",
      "valueRange" : "Range",
      "valueRatio" : "Ratio",
      "valueSampledData" : "SampledData",
      "valueAttachment" : "Attachment",
      "valueTime" : "time",
      "valueDateTime" : "dateTime",
      "valuePeriod" : "Period",
      "dataAbsentReason" : "CodeableConcept",
      "interpretation" : "CodeableConcept",
      "comments" : "string",
      "bodySite" : "CodeableConcept",
      "method" : "CodeableConcept",
      "specimen" : "Reference",
      "device" : "Reference",
      "referenceRange" : [{
        "low" : "Quantity",
        "high" : "Quantity",
        "meaning" : "CodeableConcept",
        "age" : "Range",
        "text" : "string"
      }],
      "related" : [{
        "type" : "code",
        "target" : "Reference"
      }],
      "component" : [{
        "code" : "CodeableConcept",

        "valueQuantity" : "Quantity",
        "valueCodeableConcept" : "CodeableConcept",
        "valueString" : "string",
        "valueRange" : "Range",
        "valueRatio" : "Ratio",
        "valueSampledData" : "SampledData",
        "valueAttachment" : "Attachment",
        "valueTime" : "time",
        "valueDateTime" : "dateTime",
        "valuePeriod" : "Period",
        "dataAbsentReason" : "CodeableConcept",
        "referenceRange" :  [{
          "low" : "Quantity",
          "high" : "Quantity",
          "meaning" : "CodeableConcept",
          "age" : "Range",
          "text" : "string"
        }]
      }],
      "extension":["extension"]
    },

    "extension":{
      "url" : "uri",
      "valueInteger" : "integer",
      "valueDecimal" : "decimal",
      "valueDateTime" : "dateTime",
      "valueDate" : "date",
      "valueInstant" : "instant",
      "valueString" : "string",
      "valueUri" : "uri",
      "valueBoolean" : "boolean",
      "valueCode" : "code",
      "valueBase64Binary" : "base64Binary",
      "valueCoding" : "Coding",
      "valueCodeableConcept" : "CodeableConcept",
      "valueAttachment" : "Attachment",
      "valueIdentifier" : "Identifier",
      "valueQuantity" : "Quantity",
      "valueRange" : "Range",
      "valuePeriod" : "Period",
      "valueRatio" : "Ratio",
      "valueHumanName" : "HumanName",
      "valueAddress" : "Address",
      "valueContactPoint" : "ContactPoint",
      "valueSchedule" : "Schedule",
      "valueReference" : "Reference"
    },

    "Sequence":{
        "type":"code",
        "patient":"Reference",
        "specimen":"Reference",
        "device":"Reference",
        "quantity":"Quantity",
        "species":"CodeableConcept",
        "variation":{
            "start":"integer",
            "end":"integer",
            "observedAllele":"string",
            "referenceAllele":"string",
            "cigar":"string"
        },
        "quality":{
            "start":"integer",
            "end":"integer",
            "score":"Quantity",
            "method":"string"
        },
        "allelicState":"CodeableConcept",
        "readCoverage":"integer",
        "pointer":["Reference"],
        "observedSeq":"string",
        "ovservation":"Reference",
        "structureVariation":{
            "precisionOfBoundaries":"string",
            "reportedaCGHRation":"decimal",
            "length":"integer",
            "outer":{
                "start":"integer",
                "end":"integer"
            },
            "inner":{
                "start":"integer",
                "end":"integer"
            }
        }
    },

    "sequence":{
      "resourceType" : "string",
      "type" : "code",
      "patient" : "Reference",
      "specimen" : "Reference",
      "device" : "Reference",
      "quantity" : "Quantity",
      "species" : "CodeableConcept",
      "referenceSeq" : [{
        "chromosome" : "CodeableConcept",
        "genomeBuild" : "string",
        "referenceSeqId" : "CodeableConcept",
        "referenceSeqPointer" : "Reference",
        "referenceSeqString" : "string",
        "windowStart" : "integer",
        "wexampleindowEnd" : "integer"
      }],
      "variation" : {
        "start" : "integer",
        "end" : "integer",
        "observedAllele" : "string",
        "referenceAllele" : "string",
        "cigar" : "string"
      },
      "quality" : [{
        "start" : "integer",
        "end" : "integer",
        "score" : "Quantity",
        "method" : "string"
      }],
      "allelicState" : "CodeableConcept",
      "allelicFrequency" : "decimal",
      "copyNumberEvent" : "CodeableConcept",
      "readCoverage" : "integer",
      "repository" : [{
        "url" : "uri",
        "name" : "string",
        "variantId" : "string",
        "readId" : "string"
      }],
      "pointer" : ["Reference"],
      "observedSeq" : "string",
      "observation" : "Reference",
      "structureVariation" : {
        "precisionOfBoundaries" : "string",
        "reportedaCGHRatio" : "decimal",
        "length" : "integer",
        "outer" : {
          "start" : "integer",
          "end" : "integer"
        },
        "inner" : {
          "start" : "integer",
          "end" : "integer"
        }
      }
    }

    }
    '''
)

masked_title = 'Why I see this marker?'

masked_info = 'The content you are about to see is protected under the privacy policy issued by patient itself.'

masked_mark = 'Content can not display'

basic_type = ['boolean','integer','string','decimal','uri','base64Binary','instant','date','dateTime','time','code','oid','id','markdown','unsignedInt','positiveInt']

primary_key = {'HumanName':'use','name':'use','identifier':'use','address':'use','telecom':'use','valueContactPoint':'use'}

complex_key = ['name','telecom','contact','address','animal','communication','maritalStatus']
simple_key = ['gender','birthDate']
choice_key = {'multipleBirth':['multipleBirthBoolean','multipleBirthInteger'],'deceased':['deceasedBoolean','deceasedDateTime']}

def get_option():
    """

    :return:list of key, item in the list is the field that doctor can choose to see
    """
    return complex_key+simple_key+choice_key.keys()

def extend_option(form):
    """

    :param form: form submit from doctor
    :return: list of key, item in the list is the field that doctor has choose,
            and selected item in choice_key will be extented to it's value
    """
    keys = []
    for field in form:
        if field.type =='BooleanField' and field.data == True:
            key = field.name
            if key in choice_key.keys():
                keys = keys + choice_key[key]
            elif key in complex_key or key in simple_key:
                keys.append(key)
    return keys
