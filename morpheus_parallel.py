from functools import partial
from itertools import starmap
from turtle import update

import manim as mn
import manimpango as mp

class MorpheusParallel(mn.Scene):
    def construct(self):

        # slide background color
        self.camera.background_color = "#212121ff"

        text_f = partial(mn.Text, font="Helvetica")

        # Draw Base Image ======================================================
        base_image = mn.Square(side_length=4, color=mn.WHITE, fill_opacity=1).set_fill(mn.GRAY_A)
        base_text = text_f("Large Image", font="Helvetica").next_to(base_image, mn.UP)
        self.play(mn.FadeIn(base_image), mn.FadeIn(base_text))

        self.wait(1)

        # Split into sub images ================================================
        r_kwargs = dict(
            height=1, width=4, color=mn.WHITE, fill_opacity=1, fill_color=mn.GRAY_A
        )
        sub_images = [mn.Rectangle(**r_kwargs) for _ in range(4)]
        directions = [mn.UP, mn.UP, mn.DOWN, mn.DOWN]
        shifts = [1.5, .5, .5, 1.5]
        list(starmap(lambda i, d, s: i.shift(d * s), zip(sub_images,directions,shifts)))
        sub_image_text = [text_f("Sub-Image").next_to(sub_images[i]) for i in range(4)]
        self.play(
            *[mn.DrawBorderThenFill(s) for s in sub_images],
        )
        self.wait(0.25)

        self.play(
            *[mn.FadeIn(s) for s in sub_image_text]
        )

        self.play(mn.FadeOut(base_image), mn.FadeOut(base_text))
        self.wait(0.25)


        # spread sub images ====================================================
        shifts = [0.75, 0.25, 0.25, 0.75]
        self.play(
            *list(starmap(lambda i, d, s: i.animate.shift(d*s), zip(sub_images, directions, shifts))),
            *list(starmap(lambda i, d, s: i.animate.shift(d*s), zip(sub_image_text, directions, shifts)))
        )

        self.play(*list(map(lambda t: mn.FadeOut(t), sub_image_text)))

        # show model as a square and duplicate =================================
        model_kwargs = dict(side_length=1.25, color=mn.ORANGE)
        models = [mn.Square(**model_kwargs).next_to(sub_images[-1], mn.LEFT) for _ in range(4)]
        model_text = text_f("Model").next_to(models[0], mn.LEFT)
        self.play(
            *list(map(lambda m: mn.FadeIn(m), models + [model_text]))
        )
        self.wait(0.25)
        shifts = [1.5, 3, 4.5]
        self.play(*list(starmap(lambda r, s: r.animate.shift(mn.UP * s), zip(models[1:], shifts))))

        self.wait(0.25)
        model_copy = [text_f("Copy").next_to(models[i], mn.LEFT) for i in range(1, 4)]
        self.play(
            *list(map(lambda r: mn.FadeIn(r), model_copy))
        )

        self.wait(0.25)
        self.play(
            *list(map(lambda s: mn.FadeOut(s), model_copy + [model_text]))
        )

        # move model over rectangle and change color ===========================

        #https://stackoverflow.com/a/59958915
        classified_sub_images = [s.copy().set_fill(mn.ORANGE,1) for s in sub_images]
        for s,c in zip(sub_images, classified_sub_images):
            s.z_index = 1
            c.z_index = 0
        list(map(lambda s: s.stretch_to_fit_width(0.01), classified_sub_images))
        self.add(*classified_sub_images)

        list(map(lambda s: s.generate_target(), classified_sub_images))

        def update_f(sub_image, mob, alpha):
            mob.become(mob.target)
            mob.stretch_to_fit_width(alpha * sub_image.get_width()).next_to(sub_image.get_left(), mn.RIGHT, buff=0)
            mob.next_to(sub_image.get_left(), mn.RIGHT, buff=0)

        update_fs = [partial(update_f, s) for s in sub_images]

        classify_text = text_f("Classify in Parallel").next_to(classified_sub_images[0], mn.UP)
        self.play(mn.FadeIn(classify_text))

        for c in classified_sub_images:
            c.z_index = 1
        self.play(
            *list(map(lambda r: r.animate.shift(mn.RIGHT * 6), models)),
            *list(starmap(lambda c,f: mn.UpdateFromAlphaFunc(c, f), zip(classified_sub_images,update_fs))),
        )

        self.wait(0.50)
        stitch_text = text_f("Stitch Images Back Together").next_to(classified_sub_images[0], mn.UP).next_to(classified_sub_images[0], mn.UP)

        self.play(*list(map(lambda s: mn.FadeOut(s), sub_images + [classify_text] + models)), mn.FadeIn(stitch_text))

        # Stitch back together
        shifts = [0.75, 0.25, 0.25, 0.75]
        self.play(
            *list(starmap(lambda i, d, s: i.animate.shift(d*s), zip(classified_sub_images, directions[::-1], shifts))),
        )


        base_image.set_fill(mn.ORANGE, 1)
        self.play(mn.FadeIn(base_image))
        self.play(
            *list(map(lambda c: mn.FadeOut(c), classified_sub_images)),
        )

        self.wait(1)




if __name__=="__main__":
    import subprocess
    subprocess.run([
        "manim",
        "-pql",
        "--format=gif",
        "morpheus_parallel.py",
        "MorpheusParallel"
    ])