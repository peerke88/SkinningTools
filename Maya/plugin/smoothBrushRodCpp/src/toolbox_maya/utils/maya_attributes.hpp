#pragma once
#include <maya/MPlug.h>

/// @return the MPlug of an "attribute" of a dependency "node"
MPlug get_plug(const MObject& node, const MString& attribute);

/// @return the MPlug of an "attribute" of a dependency "node"
MPlug get_plug(const MObject& node, const MObject& attribute);

bool is_connected(const MPlug& plug);


// -----------------------------------------------------------------------------

void connect(const MPlug& source_plug, const MPlug& dest_plug);

void connect(const MObject& source_obj, const MString& src_plug_name,
             const MObject& dest_obj  , const MString& dest_plug_name);

void connect(const MObject& source_obj, const MObject& src_attribute,
             const MObject& dest_obj  , const MString& dest_plug_name);

void connect(const MObject& source_obj, const MString& src_plug_name,
             const MObject& dest_obj  , const MObject& dest_attribute);

void connect(const MObject& source_obj, const MObject& src_plug_name,
             const MObject& dest_obj  , const MObject& dest_attribute);

// -----------------------------------------------------------------------------

void disconnect(const MPlug& source_plug, const MPlug& dest_plug);

void disconnect(const MObject& source_obj, const MString& src_plug_name,
                const MObject& dest_obj  , const MString& dest_plug_name);

void disconnect(const MObject& source_obj, const MObject& src_attribute,
                const MObject& dest_obj  , const MString& dest_plug_name);

void disconnect(const MObject& source_obj, const MString& src_plug_name,
                const MObject& dest_obj  , const MObject& dest_attribute);

void disconnect(const MObject& source_obj, const MObject& src_plug_name,
                const MObject& dest_obj  , const MObject& dest_attribute);

// -----------------------------------------------------------------------------

