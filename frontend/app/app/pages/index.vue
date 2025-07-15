<template>
  <div class="flex flex-col items-center justify-center gap-4 py-16">
    <div class="text-center">
      <h1 class="font-bold text-3xl text-default mb-2">Auto Labeling App</h1>
      <p class="text-muted text-lg">Image labeling made easier</p>
    </div>

    <div class="flex flex-col items-center gap-4 p-8 bg-default rounded-lg  border border-accented">

      <SignedOut>
        <SignInButton
          mode="modal"
          after-sign-in-url="/dataset"
        >
          <UButton
            label="Sign In to Continue"
            icon="i-lucide-log-in"
            size="lg"
            color="primary"
            class="px-8 py-3"
          />
        </SignInButton>
      </SignedOut>

      <SignedIn>
        <div class="text-center">
          <p class="text-muted mb-4">Welcome back!</p>
          <UButton
            label="Go to Datasets"
            icon="i-lucide-folder"
            size="lg"
            color="primary"
            to="/dataset"
            class="px-8 py-3"
          />
        </div>
      </SignedIn>
    </div>
  </div>
</template>
