
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
// uniform vec3 ambient;
uniform vec3 cameraPosition;

uniform bool useTexture;   // toggle for texture or pure color
uniform vec3 baseColor;    // color for untextured objects

out vec4 color;

vec3 calculatePointLight(PointLight light, vec3 fragPos, vec3 normal, vec3 viewDir) {
    
    // Light direction
    vec3 lightDir = light.position - fragPos;
    float distance = length(lightDir);
    lightDir = normalize(lightDir);

    // Diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);

    // Specular shading (Blinn-Phong)
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(normal, halfwayDir), 0.0), 32.0);

    // Attenuation (inverse-square falloff)
    float attenuation = 1.0 / (distance * distance);

    // Combine results
    vec3 diffuse = diff * light.color * light.strength;
    vec3 specular = spec * light.color * light.strength;

    return (diffuse + specular) * attenuation;
}

void main()
{

    // Texture color
    vec4 texColor = texture(imageTexture, fragmentTexCoord);
    vec3 baseColor = texColor.rgb;

    // Normalized normal from vertex shader
    vec3 normal = normalize(fragmentNormal);

    // View direction
    vec3 viewDir = normalize(cameraPosition - fragmentPosition);

    // Ambient term
    vec3 ambient = 0.3 * baseColor;

    // Accumulate light contributions
    vec3 lighting = ambient;


    for (int i = 0; i < 8; i++) {
        lighting += calculatePointLight(Lights[i], fragmentPosition, normal, viewDir) * baseColor;
    }

    
    color = vec4(lighting, texColor.a);
    // color = vec4(normal, texColor.a);
}

