import arcpy
import datetime
import sys


def spatialJoins(WUD_PARCELS, PARCEL_COPY, CIS_XY, PZB_CCRT_AREAS, PBCWUD_ZONES, WUD_LiftstationBoundaries, PZB_ZONING, workspaceforCodes):

    # # Process: Copy (Copy) (management)
    # if arcpy.Exists(PARCEL_COPY):
    #     arcpy.DeleteFeatures_management(PARCEL_COPY)
    #     arcpy.management.Copy(WUD_PARCELS, PARCEL_COPY)
    # else:
    #     arcpy.AddMessage("Creating copy of PARCEL_COPY")
    #     print("Creating copy of PARCEL_COPY")
    #     arcpy.management.Copy(WUD_PARCELS, PARCEL_COPY)
    # print("Creating Spatial index of PARCEL Copy.")
    # arcpy.AddSpatialIndex_management(PARCEL_COPY)

    WUD_PARCELS_wCIS_XY = workspaceforCodes + "\\WUD_PARCELS_wCIS_XY"
    WUD_PARCELS_wCCRT_AREAS = workspaceforCodes + "\\WUD_PARCELS_wCCRT_AREAS"
    WUD_PARCELS_wZONES = workspaceforCodes + "\\WUD_PARCELS_wZONES"
    WUD_PARCELS_wLSBoundaries = workspaceforCodes + "\\WUD_PARCELS_wLSBoundaries"
    WUD_PARCELS_wZONING = workspaceforCodes + "\\WUD_PARCELS_wZONING"

    Field_Map = "PARID \"PARID\" true true false 17 Text 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                "\\WUD_PARCELS,PARID,0,17;CITY_CODE \"CITY_CODE\" true true false 2 Text 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                "\\WUD_PARCELS,CITY_CODE,0,2;SITE_ADDR_STR \"SITE_ADDR_STR\" true true false 121 Text 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                "\\WUD_PARCELS,SITE_ADDR_STR,0,121;MUNICIPALITY \"MUNICIPALITY\" true true false 40 Text 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                "\\WUD_PARCELS,MUNICIPALITY,0,40;CRA \"CRA\" true true false 20 Text 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                "\\WUD_PARCELS,CRA,0,20;ACRES \"ACRES\" true true false 255 Text 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                "\\WUD_PARCELS,ACRES,-1,-1;SUBDIV_NAME \"SUBDIV_NAME\" true true false 255 Text 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                "\\WUD_PARCELS,SUBDIV_NAME,0,2000;IMPRV_MRKT \"IMPRV_MRKT\" true true false 4 Float 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                "\\WUD_PARCELS,IMPRV_MRKT,-1,-1;PROPERTY_USE \"PROPERTY_USE\" true true false 40 Text 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                "\\WUD_PARCELS,PROPERTY_USE,0,40;SERVICE_TYPE \"SERVICE_TYPE\" true true false 4000 Text 0 0,First,#," \
                "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\CIS_to_GIS_Point.gdb\\CIS_XYdatamapped," \
                "SERVICE_TYPE,0,4000"
    Field_Map_2 = "PARID \"PARID\" true true false 17 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCIS_XY,PARID,0,17;CITY_CODE \"CITY_CODE\" true true false 2 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCIS_XY,CITY_CODE,0,2;SITE_ADDR_STR \"SITE_ADDR_STR\" true true false 121 Text 0 0," \
                   "First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCIS_XY,SITE_ADDR_STR,0,121;MUNICIPALITY \"MUNICIPALITY\" true true false 40 Text 0 " \
                   "0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status" \
                   ".gdb\\WUD_PARCELS_wCIS_XY,MUNICIPALITY,0,40;CRA \"CRA\" true true false 20 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCIS_XY,CRA,0,20;ACRES \"ACRES\" true true false 255 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCIS_XY,ACRES,0,255;SUBDIV_NAME \"SUBDIV_NAME\" true true false 255 Text 0 0,First," \
                   "#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCIS_XY,SUBDIV_NAME,0,255;IMPRV_MRKT \"IMPRV_MRKT\" true true false 4 Float 0 0," \
                   "First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCIS_XY,IMPRV_MRKT,-1,-1;PROPERTY_USE \"PROPERTY_USE\" true true false 40 Text 0 0," \
                   "First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCIS_XY,PROPERTY_USE,0,40;SERVICE_TYPE \"SERVICE_TYPE\" true true false 4000 Text 0 " \
                   "0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status" \
                   ".gdb\\WUD_PARCELS_wCIS_XY,SERVICE_TYPE,0,4000;CCRTNAME \"CCRTNAME\" true true false 35 Text 0 0," \
                   "First,#,W:\\GIS\\Database Connections\\PBCGIS - GISPROD.sde\\PZB.CCRT_AREAS,FNAME,0,35;CCRTCODE " \
                   "\"CCRTCODE\" true true false 5 Text 0 0,First,#,W:\\GIS\\Database Connections\\PBCGIS - " \
                   "GISPROD.sde\\PZB.CCRT_AREAS,FCODE,0,5;CCRTTYPE \"CCRTTYPE\" true true false 100 Text 0 0,First,#," \
                   "W:\\GIS\\Database Connections\\PBCGIS - GISPROD.sde\\PZB.CCRT_AREAS,CCRT_TYPE,0,100"
    Field_Map_3 = "PARID \"PARID\" true true false 17 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,PARID,0,17;CITY_CODE \"CITY_CODE\" true true false 2 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,CITY_CODE,0,2;SITE_ADDR_STR \"SITE_ADDR_STR\" true true false 121 Text " \
                   "0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status" \
                   ".gdb\\WUD_PARCELS_wCCRT_AREAS,SITE_ADDR_STR,0,121;MUNICIPALITY \"MUNICIPALITY\" true true false " \
                   "40 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,MUNICIPALITY,0,40;CRA \"CRA\" true true false 20 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,CRA,0,20;ACRES \"ACRES\" true true false 255 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,ACRES,0,255;SUBDIV_NAME \"SUBDIV_NAME\" true true false 255 Text 0 0," \
                   "First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,SUBDIV_NAME,0,255;IMPRV_MRKT \"IMPRV_MRKT\" true true false 4 Float 0 " \
                   "0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status" \
                   ".gdb\\WUD_PARCELS_wCCRT_AREAS,IMPRV_MRKT,-1,-1;PROPERTY_USE \"PROPERTY_USE\" true true false 40 " \
                   "Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,PROPERTY_USE,0,40;SERVICE_TYPE \"SERVICE_TYPE\" true true false 4000 " \
                   "Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,SERVICE_TYPE,0,4000;CCRTNAME \"CCRTNAME\" true true false 35 Text 0 0," \
                   "First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,CCRTNAME,0,35;CCRTCODE \"CCRTCODE\" true true false 5 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,CCRTCODE,0,5;CCRTTYPE \"CCRTTYPE\" true true false 100 Text 0 0,First," \
                   "#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wCCRT_AREAS,CCRTTYPE,0,100;ZONE \"ZONE\" true true false 2 Short 0 5,First,#," \
                   "W:\\GIS\\Database Connections\\wGISMaps@GISagl.WUD.sde\\wGISMaps.WUD.Boundaries\\wGISMaps.WUD" \
                   ".PBCWUD_ZONES,ZONE_,-1,-1"
    Field_Map_4 = "PARID \"PARID\" true true false 17 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\" \
                  "Workspaces\\WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,PARID,0,17;CITY_CODE \"CITY_CODE\"" \
                  " true true false 2 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,CITY_CODE,0,2;SITE_ADDR_STR \"SITE_ADDR_STR\"" \
                  " true true false 121 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,SITE_ADDR_STR,0,121;MUNICIPALITY" \
                  " \"MUNICIPALITY\" true true false 40 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\" \
                  "Workspaces\\WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,MUNICIPALITY,0,40;CRA \"CRA\"" \
                  " true true false 20 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,CRA,0,20;ACRES \"ACRES\" true true false 255" \
                  " Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,ACRES,0,255;SUBDIV_NAME \"SUBDIV_NAME\" true" \
                  " true false 255 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,SUBDIV_NAME,0,255;IMPRV_MRKT \"IMPRV_MRKT\"" \
                  " true true false 4 Float 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,IMPRV_MRKT,-1,-1;PROPERTY_USE \"PROPERTY_USE\"" \
                  " true true false 40 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,PROPERTY_USE,0,40;SERVICE_TYPE \"SERVICE_TYPE\"" \
                  " true true false 4000 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,SERVICE_TYPE,0,4000;CCRTNAME \"CCRTNAME\" true" \
                  " true false 35 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,CCRTNAME,0,35;CCRTCODE \"CCRTCODE\" true true" \
                  " false 5 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,CCRTCODE,0,5;CCRTTYPE \"CCRTTYPE\" true true" \
                  " false 100 Text 0 0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,CCRTTYPE,0,100;ZONE \"ZONE\" true true false" \
                  " 2 Short 0 5,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\" \
                  "WUD_Properties_Service_Status.gdb\\WUD_PARCELS_wZONES,ZONE,-1,-1;LS_No \"LS_No\" true true false 4" \
                  " Long 0 10,First,#,W:\\GIS\\Database Connections\\wGISMaps@GISagl.WUD.sde\\" \
                  "wGISMaps.WUD.SewerStormwater\\wGISMaps.WUD.ssLiftStationsBoundaries,LS_No,-1,-1;LS_FacilityID" \
                  " \"LS_FacilityID\" true true false 20 Text 0 0,First,#,W:\\GIS\\Database Connections\\" \
                  "wGISMaps@GISagl.WUD.sde\\wGISMaps.WUD.SewerStormwater\\wGISMaps.WUD.ssLiftStationsBoundaries,LS_FacilityID,0,20"
    Field_Map_5 = "PARID \"PARID\" true true false 17 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,PARID,0,17;CITY_CODE \"CITY_CODE\" true true false 2 Text 0 0,First," \
                   "#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,CITY_CODE,0,2;SITE_ADDR_STR \"SITE_ADDR_STR\" true true false 121 " \
                   "Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,SITE_ADDR_STR,0,121;MUNICIPALITY \"MUNICIPALITY\" true true false 40 " \
                   "Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,MUNICIPALITY,0,40;CRA \"CRA\" true true false 20 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,CRA,0,20;ACRES \"ACRES\" true true false 255 Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,ACRES,0,255;SUBDIV_NAME \"SUBDIV_NAME\" true true false 255 Text 0 0," \
                   "First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,SUBDIV_NAME,0,255;IMPRV_MRKT \"IMPRV_MRKT\" true true false 4 Float 0 " \
                   "0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status" \
                   ".gdb\\WUD_PARCELS_wLSBoundaries,IMPRV_MRKT,-1,-1;PROPERTY_USE \"PROPERTY_USE\" true true false 40 " \
                   "Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,PROPERTY_USE,0,40;SERVICE_TYPE \"SERVICE_TYPE\" true true false 4000 " \
                   "Text 0 0,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,SERVICE_TYPE,0,4000;CCRTNAME \"CCRTNAME\" true true false 35 Text 0 " \
                   "0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status" \
                   ".gdb\\WUD_PARCELS_wLSBoundaries,CCRTNAME,0,35;CCRTCODE \"CCRTCODE\" true true false 5 Text 0 0," \
                   "First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,CCRTCODE,0,5;CCRTTYPE \"CCRTTYPE\" true true false 100 Text 0 0," \
                   "First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,CCRTTYPE,0,100;ZONE \"ZONE\" true true false 2 Short 0 5,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,ZONE,-1,-1;LS_No \"LS_No\" true true false 4 Long 0 10,First,#," \
                   "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb" \
                   "\\WUD_PARCELS_wLSBoundaries,LS_No,-1,-1;LS_FacilityID \"LS_FacilityID\" true true false 20 Text 0 " \
                   "0,First,#,W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status" \
                   ".gdb\\WUD_PARCELS_wLSBoundaries,LS_FacilityID,0,20;ZONINGDESC \"ZONINGDESC\" true true false 100 " \
                   "Text 0 0,First,#,W:\\GIS\\Database Connections\\PBCGIS - GISPROD.sde\\PZB.ZONING,ZONING_DESC,0," \
                   "100;ZONINGNAME \"ZONINGNAME\" true true false 90 Text 0 0,First,#,W:\\GIS\\Database " \
                   "Connections\\PBCGIS - GISPROD.sde\\PZB.ZONING,FNAME,0,90;ZONINGCODE \"ZONINGCODE\" true true " \
                   "false 50 Text 0 0,First,#,W:\\GIS\\Database Connections\\PBCGIS - GISPROD.sde\\PZB.ZONING,FCODE," \
                   "0,50"


    # Process: Spatial Join (Spatial Join) (analysis)
    arcpy.AddMessage("Creating CIS_XY join.")
    print("Creating CIS_XY join.")
    arcpy.analysis.SpatialJoin(target_features=WUD_PARCELS, join_features=CIS_XY,
                               out_feature_class=WUD_PARCELS_wCIS_XY, field_mapping=Field_Map,
                               match_option="INTERSECT", search_radius="0 Feet")

    # Process: Spatial Join (2) (Spatial Join) (analysis)
    arcpy.AddMessage("Creating PZB_CCRT_AREAS join.")
    print("Creating PZB_CCRT_AREAS join.")
    arcpy.analysis.SpatialJoin(target_features=WUD_PARCELS_wCIS_XY, join_features=PZB_CCRT_AREAS,
                               out_feature_class=WUD_PARCELS_wCCRT_AREAS, field_mapping=Field_Map_2,
                               match_option="HAVE_THEIR_CENTER_IN")

    # Process: Spatial Join (3) (Spatial Join) (analysis)
    arcpy.AddMessage("Creating PBCWUD_ZONES join.")
    print("Creating PBCWUD_ZONES join.")
    arcpy.analysis.SpatialJoin(target_features=WUD_PARCELS_wCCRT_AREAS, join_features=PBCWUD_ZONES,
                               out_feature_class=WUD_PARCELS_wZONES, field_mapping=Field_Map_3,
                               match_option="HAVE_THEIR_CENTER_IN")

    # Process: Spatial Join (4) (Spatial Join) (analysis)
    arcpy.AddMessage("Creating LiftstationBoundaries join.")
    print("Creating LiftstationBoundaries join.")
    arcpy.analysis.SpatialJoin(target_features=WUD_PARCELS_wZONES, join_features=WUD_LiftstationBoundaries,
                               out_feature_class=WUD_PARCELS_wLSBoundaries, field_mapping=Field_Map_4,
                               match_option="HAVE_THEIR_CENTER_IN")

    # Process: Spatial Join (5) (Spatial Join) (analysis)
    arcpy.AddMessage("Creating PZB_ZONING join.")
    print("Creating PZB_ZONING join.")
    arcpy.analysis.SpatialJoin(target_features=WUD_PARCELS_wLSBoundaries, join_features=PZB_ZONING,
                               out_feature_class=WUD_PARCELS_wZONING, field_mapping=Field_Map_5,
                               match_option="HAVE_THEIR_CENTER_IN")

    new_Fields = [["WATER100", "TEXT", "WATER100", "5", "", ""], ["WATER100500", "TEXT", "WATER100500", "5", "", ""], ["WATERgreater500", "TEXT", "WATERgreater500", "5", "", ""]]
    WUD_Properties_Status_Info = workspaceforCodes + "\\WUD_Properties_Service_Status"

    # Copying New/Overwriting WUD_Properties_Service_Status layer
    arcpy.AddMessage("Creating final feature class and adding Water distance fields.")
    arcpy.management.Copy(WUD_PARCELS_wZONING, WUD_Properties_Status_Info)
    arcpy.AddFields_management(WUD_Properties_Status_Info, field_description=new_Fields)

    return (WUD_PARCELS_wCIS_XY, WUD_PARCELS_wCCRT_AREAS, WUD_PARCELS_wZONES, WUD_PARCELS_wLSBoundaries,
            WUD_PARCELS_wZONING, WUD_Properties_Status_Info)


def waterFields(WUD_Properties_Status_Info):

    print('Calculating distance to water pipes, potable, 12" and under.')
    arcpy.AddMessage('Calculating distance to water pipes, potable, 12" and under.')

    WUD_PotableWater = r"W:\GIS\Database Connections\GISdb_wGISProd.OSA.sde\wGISProd.WUD.WaterDistribution\wGISProd.WUD.wMain"

    water_Query = "LIFECYCLESTATUS = 'ACTIVE' And WATERTYPE = 'Potable' And OWNEDBY = 1 And MAINTBY = 1 And DIAMETER <= 12"

    arcpy.MakeFeatureLayer_management(WUD_Properties_Status_Info, "WUD_Properties_Status_Info")
    arcpy.MakeFeatureLayer_management(WUD_PotableWater, "WUD_PotableWater", water_Query)

    # arcpy.analysis.Near(
    #     in_features="WUD_Properties_Status_Info",
    #     near_features="WUD_PotableWater",
    #     search_radius="500 Feet",
    #     location="NO_LOCATION",
    #     angle="NO_ANGLE",
    #     method="PLANAR",
    #     field_names="NEAR_FID NEAR_FID;NEAR_DIST NEAR_DIST",
    #     distance_unit="Feet"
    # )

    arcpy.analysis.Near("WUD_Properties_Status_Info",
                        "WUD_PotableWater",
                        "500 Feet",
                        "NO_LOCATION",
                        "NO_ANGLE",
                        "PLANAR",
                        "NEAR_FID NEAR_FID;NEAR_DIST NEAR_DIST")


    with arcpy.da.UpdateCursor(WUD_Properties_Status_Info, ["WATER100", "WATER100500", "WATERgreater500", "NEAR_DIST"]) as cursor:
        for row in cursor:
            if 0 <= row[3] <= 100:
                row[0] = 'YES'
                row[1] = 'NO'
                row[2] = 'NO'
            elif 100 < row[3] <= 500:
                row[0] = 'NO'
                row[1] = 'YES'
                row[2] = 'NO'
            elif row[3] == -1:
                row[0] = 'NO'
                row[1] = 'NO'
                row[2] = 'YES'
            else:
                pass
            cursor.updateRow(row)

    arcpy.management.DeleteField(WUD_Properties_Status_Info, "Join_Count;TARGET_FID;NEAR_FID;NEAR_DIST", "DELETE_FIELDS")


def updatePropertyStatusInfo(WUD_PARCELS_wCIS_XY, WUD_PARCELS_wCCRT_AREAS, WUD_PARCELS_wZONES, WUD_PARCELS_wLSBoundaries, WUD_PARCELS_wZONING, WUD_Properties_Status_Info):


    try:

        arcpy.env.workspace = r"W:\GIS\Database Connections\GISagl_wGISMaps.WUD.sde"
        PropertyStatusInfo = r"W:\GIS\Database Connections\GISagl_wGISMaps.WUD.sde\wGISMaps.WUD.CIS\PropertyStatusInfo"

        print("Deleting old features from local dataset")
        arcpy.AddMessage("Deleting old features from local dataset")
        deleteOld = arcpy.DeleteFeatures_management(PropertyStatusInfo)

        if deleteOld:
            print("Starting Append process.")
            arcpy.AddMessage("Starting Append process.")
            appendDone = arcpy.Append_management(WUD_Properties_Status_Info, PropertyStatusInfo, "NO_TEST")
            if appendDone:
                # do clean up
                print("Append complete. WUD.MUNICIPALITIES have been updated according to PBCGIS data.")
                print("Cleaning up tempDatabase." + "\n")
                arcpy.AddMessage("Append complete.  Cleaning up tempDatabase.")
                arcpy.DeleteFeatures_management(WUD_PARCELS_wCIS_XY)
                arcpy.DeleteFeatures_management(WUD_PARCELS_wCCRT_AREAS)
                arcpy.DeleteFeatures_management(WUD_PARCELS_wZONES)
                arcpy.DeleteFeatures_management(WUD_PARCELS_wLSBoundaries)
                arcpy.DeleteFeatures_management(WUD_PARCELS_wZONING)
                arcpy.DeleteFeatures_management(WUD_Properties_Status_Info)

    except():
        arcpy.AddMessage("Error in Append Process.")
        sys.exit(0)

if __name__ == '__main__':

    arcpy.env.overwriteOutput = True

    # SOURCE PATHS:
    WUD_PARCELS = "W:\\GIS\\Database Connections\\GISagl_wGISMaps.WUD.sde\\wGISMaps.WUD.LandBase\\wGISMaps.WUD.Parcels"
    CIS_XY = 'W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\CIS_to_GIS_Point.gdb\\CIS_XYdatamapped'
    PZB_CCRT_AREAS = 'W:\\GIS\\Database Connections\\PBCGIS - GISPROD.sde\\PZB.CCRT_AREAS'
    PBCWUD_ZONES = 'W:\\GIS\\Database Connections\\wGISMaps@GISagl.WUD.sde\\wGISMaps.WUD.Boundaries\\wGISMaps.WUD.PBCWUD_ZONES'
    WUD_LiftstationBoundaries = 'W:\\GIS\\Database Connections\\wGISMaps@GISagl.WUD.sde\\wGISMaps.WUD.SewerStormwater\\wGISMaps.WUD.ssLiftStationsBoundaries'
    PZB_ZONING = 'W:\\GIS\\Database Connections\\PBCGIS - GISPROD.sde\\PZB.ZONING'

    # WORKING/BACKUP PATHS:
    workspaceforCodes = "W:\\GIS\\Scripts\\Scheduled_Scripts_GISLIC\\Workspaces\\WUD_Properties_Service_Status.gdb"
    PARCEL_COPY = workspaceforCodes + "\\WUD_PARCELS"

    startTime = datetime.datetime.now().replace(microsecond=0)
    print("Operation started on {}".format(startTime))

    WUD_PARCELS_wCIS_XY, WUD_PARCELS_wCCRT_AREAS, WUD_PARCELS_wZONES, WUD_PARCELS_wLSBoundaries, WUD_PARCELS_wZONING, WUD_Properties_Status_Info = spatialJoins(WUD_PARCELS, PARCEL_COPY, CIS_XY, PZB_CCRT_AREAS, PBCWUD_ZONES, WUD_LiftstationBoundaries, PZB_ZONING, workspaceforCodes)
    waterFields(WUD_Properties_Status_Info)
    updatePropertyStatusInfo(WUD_PARCELS_wCIS_XY, WUD_PARCELS_wCCRT_AREAS, WUD_PARCELS_wZONES,
                             WUD_PARCELS_wLSBoundaries, WUD_PARCELS_wZONING, WUD_Properties_Status_Info)

    endTime = datetime.datetime.now().replace(microsecond=0)
    dur = endTime - startTime
    dur = str(dur)
    print('Duration: {}'.format(dur))

