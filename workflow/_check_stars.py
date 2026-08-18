import manim

star_exports = set()
if hasattr(manim, '__all__'):
    star_exports.update(manim.__all__)
for attr in dir(manim):
    if not attr.startswith('_'):
        star_exports.add(attr)

print(f'Total star exports: {len(star_exports)}')

names = [
    'normalize', 'config', 'Scene', 'Square', 'Circle', 'Arc', 'Line', 'Dot',
    'ORIGIN', 'RIGHT', 'UP', 'DOWN', 'LEFT', 'TAU', 'PI',
    'VGroup', 'VMobject', 'Group', 'Mobject', 'Point',
    'Animation', 'AnimationGroup', 'Create', 'Write', 'FadeIn', 'FadeOut',
    'Rotate', 'ApplyMethod',
    'MathTex', 'Tex', 'Code', 'Text', 'MarkupText',
    'Rectangle', 'Polygon', 'Polygram', 'RegularPolygon', 'Triangle',
    'Arrow', 'Vector',
    'ManimColor', 'color_gradient', 'ORANGE', 'BLUE', 'RED', 'RED_A', 'RED_D', 'PURE_YELLOW', 'WHITE',
    'MovingCameraScene',
    'ConvertToOpenGL', 'OpenGLMobject', 'SVGMobject',
    'TexTemplate', 'TexTemplateLibrary', 'tex_to_svg_file',
    'angle_between_vectors', 'angle_of_vector', 'rotate_vector', 'z_to_vector',
    'ArrowVectorField', 'VectorizedPoint', 'ImageMobject',
    'Difference', 'Intersection',
    'linear', 'smooth', 'rush_into', 'interpolate', 'Restore',
    'tempconfig',
]

for name in sorted(set(names)):
    in_star = name in star_exports
    print(f'  {name}: {"YES" if in_star else "NO "}')