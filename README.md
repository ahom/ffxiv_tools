# ffxiv_tools

## Goals

* cli for extracting/listing files/databse/assets
* interactive console for adhoc debugging/scripting
* handle binary files format to be able to debug easily if shit happens
* web server for model viewer

## Architecture

* FileSystem
  * ArchiveFileSystem
  * DiskFileSystem

* RawData
  * FileSystemRawData

* Views
  * RawDataViews

* Texture
  * FileSystemTexture

* Model
  * FileSystemModel

* Material
  * FileSystemMaterial
