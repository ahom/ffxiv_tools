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

window.fetch('/model').then(function (data) {
    return data.json();
}).then(function (json) {
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    var controls = new THREE.OrbitControls(camera);

    var renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

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

        var material = new THREE.MeshBasicMaterial({color: 0xff0000, wireframe: true});
        meshes.push(new THREE.Mesh(geometry, material));
    });

    camera.position.z = 5;

    meshes.forEach(function (mesh) {
        scene.add(mesh);
    });

    function render() {
        requestAnimationFrame(render);

        renderer.render(scene, camera);
    }
    render();
})
