#version 330 core

struct PointLight {
    vec3 position;
    vec3 color;
    float strength;
};

in vec2 fragmentTexCoord;
in vec3 fragmentPosition;
in vec3 fragmentNormal;

uniform sampler2D imageTexture;
uniform PointLight Lights[8];

uniform vec3 cameraPosition;


out vec4 color;

void main()
{

    // Normalized normal from vertex shader
    vec3 n = normalize(fragmentNormal);

    if (n.x > 0.5)
        color = vec4(1.0, 0.2, 0.2, 1.0); // +X = red
    else if (n.x < -0.5)
        color = vec4(0.4, 0.0, 0.0, 1.0); // -X = dark red
    else if (n.y > 0.5)
        color = vec4(0.2, 1.0, 0.2, 1.0); // +Y = green
    else if (n.y < -0.5)
        color = vec4(0.0, 0.4, 0.0, 1.0); // -Y = dark green
    else if (n.z > 0.5)
        color = vec4(0.2, 0.2, 1.0, 1.0); // +Z = blue
    else if (n.z < -0.5)
        color = vec4(0.0, 0.0, 0.4, 1.0); // -Z = dark blue
    else
        color = vec4(1.0); // fallback, white
}

