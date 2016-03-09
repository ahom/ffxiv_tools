function attach_attribute(geometry, name, attr, attr_type) {
    if (attr !== undefined && attr.length > 0 && attr[0] !== null) {
        if (attr[0].length === undefined) {
            var buf = new attr_type(attr.length);
            for (var i = 0; i < attr.length; ++i) {
                buf[i] = attr[i];
            }
            geometry.addAttribute(name, new THREE.BufferAttribute(buf, 1));
        } else if (attr[0].length > 0) {
            var size = attr[0].length;
            var buf = new attr_type(attr.length * size);
            for (var i = 0; i < attr.length; ++i) {
                for (var j = 0; j < size; ++j) {
                    buf[i * size + j] = attr[i][j];
                }
            }
            geometry.addAttribute(name, new THREE.BufferAttribute(buf, size));
        }
    }
}

var scene = new THREE.Scene();
function main() {
    var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    var controls = new THREE.OrbitControls(camera);
    var renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    function onWindowResize(){
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize( window.innerWidth, window.innerHeight );
    }
    window.addEventListener( 'resize', onWindowResize, false );

    camera.position.z = 5;

    function render() {
        requestAnimationFrame(render);
        renderer.render(scene, camera);
    }
    render();
}

function display() {
    window.fetch('/model/chara/monster/m' 
            + document.getElementById('m').value 
            + '/obj/body/b' 
            + document.getElementById('b').value 
            + '/model/m'
            + document.getElementById('m').value 
            + 'b'
            + document.getElementById('b').value 
            + '.mdl').then(function (data) {
        return data.json();
    }).then(function (json) {
        scene = new THREE.Scene();

        var lod = json.lods[0];
        var meshes = [];
        
        lod.meshes.forEach(function (mesh) {
            var attrs = mesh.attributes;
            var geometry = new THREE.BufferGeometry();

            attach_attribute(geometry, 'index', attrs.indices, Uint16Array);
            attach_attribute(geometry, 'position', attrs.positions, Float32Array);
            attach_attribute(geometry, 'normal', attrs.normals, Float32Array);
            attach_attribute(geometry, 'color', attrs.colors, Uint8Array);
            attach_attribute(geometry, 'uv', attrs.uvs, Float32Array);
            attach_attribute(geometry, 'skinWeight', attrs.blend_weights, Float32Array);
            attach_attribute(geometry, 'skinIndex', attrs.blend_indices, Uint8Array);

            window.fetch('/mtrl/chara/monster/m'
                    + document.getElementById('m').value 
                    + '/obj/body/b' 
                    + document.getElementById('b').value 
                    + '/material/v'
                    + document.getElementById('v').value 
                    + mesh.material).then(function (mtrl_data) {
                return mtrl_data.json();
            }).then(function (mtrl_json) {
                tex_promises = [];
                var material = new THREE.MeshBasicMaterial();
                var attrs = [];
                for (var attr in mtrl_json.textures) {
                    attrs.push(attr);
                }
                Promise.all(attrs.map(function (attr_r) { 
                    return window.fetch('/tex/' + mtrl_json.textures[attr_r]).then(function (tex_data) {
                        return tex_data.json();
                    }).then(function (tex_json) {
                       window.fetch('/tex_data/' + mtrl_json.textures[attr_r]).then(function (tex_mipmap) {
                           return tex_mipmap.arrayBuffer();
                       }).then(function (tex_mipmap_data) {
                            tex_mipmap_data = new Uint8Array(tex_mipmap_data);
                            var format = null;
                            if (tex_json.type == 'DXT1') {
                                format = THREE.RGB_S3TC_DXT1_Format;
                            } else if (tex_json.type == 'DXT5') {
                                format = THREE.RGBA_S3TC_DXT5_Format;
                            }
                            var comp_tex = new THREE.CompressedTexture([
                                 {
                                     data: tex_mipmap_data,
                                     width: tex_json.width,
                                     height: tex_json.height,
                                     format: format
                                 }
                            ], tex_json.width, tex_json.height, format);
                            comp_tex.minFilter = THREE.LinearFilter;
                            comp_tex.needsUpdate = true;
                            if (attr_r === 'diffuse') {
                                material.map = comp_tex;
                            }
                            if (attr_r === 'specular') {
                                material.specularMap = comp_tex;
                            }
                            if (attr_r === 'normal') {
                                material.normalMap = comp_tex;
                            }
                       });
                    });
                })).then(function () {
                    var new_mesh = new THREE.Mesh(geometry, material);
                    console.log(new_mesh);
                    scene.add(new_mesh);
                });
            });
        });
    });
}

main();

